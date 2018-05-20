'''
Author: Natrayan
Description: All settings necessary to transact in mutual funds on BSEStar using its SOAP API
'''

'''
toggle for whether BSEStar's live API is being used or testing
0 = testing; 1 = live
'''
LIVE = 0    


'''
AUTH values for BSEStar
for all following- the 1st element is value for testing environment, the 2nd for live
'''

LOGOUTURL = ['http://localhost:4200/securedpg/dashboard','']