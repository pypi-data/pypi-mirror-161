import pandas as pd
import numpy as np
import numpy_financial as npf
from pyxirr import xirr
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

#Column Name of the Dataframe must be following:
#Amount of Purchased --> PurchaseAmt
#Promo Interest Rate --> IR
#Admin Fee --> AdminFee
#Annual Fee --> AnnualFee
#Promo Term --> Term
#Promo Number --> PromoTypeNo

#Replace NaN with 0 for all columns


class interest_rate:

    def __init__(self, data):
        self.data = data
    
    #converting dates into date format
    def date_convert(self):
        """
        Convert Data Structure into Python datetime object from SQL server datetime
        
        Args:
            data: Single row of dataframe object (df.iloc[0])
        Returns:
            Datetime object
        """

        d = str(self.data['PurchaseDate'])
        year = int(d[:4])
        month = int(d[4:6])
        day = int(d[6:]) 
        
        dates = date(year, month, day)
        return dates


    def monthly_payment(self):
        """
        Calculate monthly payment that must be paid to the creditor amount based on the Interest rate, Loan amount and number of loan terms

        Args:
            data: Single row of dataframe object (df.iloc[0])
        Returns:
            List: List[0]= loan amount, List[1:] = monthly payment amount
        """

        #Parameters for PMT function for the monthly payment calculation
        pv = self.data['PurchaseAmt'] + self.data['AdminFee'] + self.data['AnnualFee']
        ir = self.data['IR']
        nper = self.data['Term']
        rate = ((1+ir/365)**(365/12)-1)

        #Condition for different promotional type 
        if self.data['PromoTypeNo'] == 1:
            monthly = npf.pmt(rate =rate, nper = nper - 3, pv=pv) 
            payments = [0 if i <= 3 else round(monthly,2) for i in range(1, nper + 1)]
        else:
            monthly = npf.pmt(rate =rate, nper = nper, pv=pv)
            payments = [ round(monthly,2) for _ in range(1,nper +1)]

        #Adding the Inital loan amount in the beginning
        payments.insert(0,self.data['PurchaseAmt'])
        return payments

    
    def int_rate(self, interest, date_diff, balance):
        """
        Amount of Interest that is paid off from the overall loan balance

        Args:
            interest (float): Daily Interest Rate (Promotional Interest Rate / 365)
            date_diff (int): Difference between the current date and a month before
            balance(float): Balance remaining as of current date (Balance = Previous month balance + Interest Accrued - Monthly Payment)
        """
        return round(((1+interest)**(date_diff)-1)*balance,2)


    def grace(self):
        """
        Checking for the Promotype (Grace vs EMP) and assigns appropriate value to the parameter for npv calculation

        Args:
            data: Single row of dataframe object (df.iloc[0])
        Returns:
            mp (list): Monthly payment amount from Purchase date to the last term that makes the interest paid = 0
            initial(datetime): Datetime object that indicates the purchase date
            d(list): Dates over the entire loan term 
            idx: Index number that is used in the internal rate of return calculation logic
        """
        data = self.data.squeeze()
        initial = self.date_convert()
        if data['PromoTypeNo'] ==  1:
            mp = [0] * 3
            d = [self.date_convert() + relativedelta(months = i) for i in range(1,4)]
            idx = 4
            return mp, initial, d, idx
        else:
            return [], initial, [], 1
    
    def internal_rate_return (self, return_dates = False):
        """
        Calculates the Internal Rate of Return (Overall Interest Rate) that is paid by the customer. AKA Criminal Interest Rate Calculation

        Args:
            data: Single row of dataframe object (df.iloc[0])
            return_dates(boolean): Defining whehter to get all the detailed information or not
        Returns:
            Rate of return: Interest rate calculated
            dates(list): datetime objects for all the dates in a list
            monthly_pay(list): list of in of payments for each month
            interests(list): Interest paid on each month
            balances(list): Remaining balance on each month
        """
        #Initializing Parameters
        data = self.data.squeeze()
        balance = data['PurchaseAmt'] + data['AdminFee'] + data['AnnualFee']
        term = data['Term']    
        ir = data['IR']
        daily_rate = ir/365    
        payment = -self.monthly_payment()[-1] 
        
        #Monthly payment, initial start date and date record (condition apply due to Grace plan)
        monthly_pay, initial_date, dates, idx = self.grace()

        #Recording the values calculated for each month for validation purpose
        balances = []
        interests = []
        diff = []
        
        #Return 0 for DP SAC Plans
        if data['PromoTypeNo'] in [6,7,9]:
            return 0         

        else:
            while balance > 0:

                #Compute the difference in dates 
                prev_date = initial_date + relativedelta(months = idx -1 )
                current_date = initial_date + relativedelta(months = idx)
                date_diff = current_date - prev_date
                diff.append(date_diff.days)

                #Calculating the interest paid for current month 
                interest = self.int_rate(daily_rate, date_diff.days, balance)
                interests.append(interest)

                #Calculating the balance as of current date (Previous Balance + Interest - Payment)
                balance = round(balance + interest - payment,2)
                balances.append(balance)
                dates.append(current_date)

                idx = idx + 1
                monthly_pay.append(-payment)

                #Condition for the last payment (Balance + Interest is less than payment then output the remainder)
                if balance + interest < payment:
                    
                    #Compute Interest Paid for the last month (it wil exceed one month from the given term)
                    ir = self.int_rate(daily_rate, date_diff.days ,balance)
                    interests.append(ir)

                    #Remainder is Balance + Interest Paid
                    remainder =round( balance + ir, 2)
                    #Remaining balance overall will be 0 
                    balances.append(0)
                    
                    #Record the remainder = last month's payment
                    monthly_pay.append(-remainder)
                    dates.append(initial_date + relativedelta(months = idx))
                    break
            
            monthly_pay.insert(0, data['PurchaseAmt'])
            dates.insert(0, self.date_convert())

            if return_dates == False:
                return xirr(dates, monthly_pay)
            return dates, diff, monthly_pay, interests, balances

    def refund_formula(self, balance, date_diff, payment):
        """
        Formula used to calculate the Max balance when the interest rate is 60%
        
        Args:
            balance(int): Previous month's max balance when 60% IR
            date_diff(int): difference between current and last month in days
            payment(float): payment amount for the current monht 
        Returns:
            Max balance at 60% (float)
        """
        return balance*(1.6)**(date_diff/365) - payment

    def refund (self):
        """ 
        Refund calculation for customers with overall of 60% or above interest rate calculation. How much to be repaid to the customer.

        Args:
            data: Single row of dataframe object (df.iloc[0])
        Returns:
            ira_record[-1](float): final refund amount when calculated for each month
        """
        data = self.data.squeeze()
        
        if data['PromoTypeNo'] in [6,7,9]:
            return 0 
            
        #Dates assignment
        date = self.internal_rate_return(return_dates = True)[0]
        
        #Last date assigned for condition
        last_date = date[-1]
        initial_date = date[0]
        
        #Monthly Payments
        m_payment = self.internal_rate_return(return_dates = True)[2]
        
        #Hash Map for Date and Payment for each month
        payments = {i.strftime('%m/%d/%Y').replace('/','') : -j for i,j in zip(date, m_payment)}

        #first new balance post one month after purchase date
        balance = data['PurchaseAmt']

        date_count = 0
        idx = 1 
        
        #One month from purcase date
        d_now = date[1]
        ira_record = []

        while d_now <= last_date :
            
            #Calculate previous date = 1month less from current date, index used to see if date should be repeated or move forward
            d_prev = d_now - relativedelta(months = 1) if date_count == 0 else d_now
            
            #Payment will be monthly pay amount but when month repeated it will be 0 
            pay = payments[d_now.strftime('%m/%d/%Y').replace('/','')] if date_count == 1 else 0

            #Date difference in days
            date_diff = (d_now - d_prev).days

            #Refund amount calculation as of current date using the formula (Update current balance as the refunded amount)
            refund_amt = self.refund_formula(balance, date_diff, pay)
            balance = refund_amt
            ira_record.append(round(balance,2))
            
            #Updating current date (idx for month calculation, date_count for current index of month)
            idx = idx + 1 if date_count == 1 else idx + 0 
            d_now = initial_date + relativedelta(months = idx) if date_count == 1 else d_now

            date_count = date_count + 1 if date_count == 0 else 0 
        
        #Transform into numpy array for conditional selection
        ira_record = np.array(ira_record)
        return ira_record[ira_record > 0][-1]