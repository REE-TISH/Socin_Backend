from rest_framework.throttling import UserRateThrottle

class DailyUserThrottle(UserRateThrottle):


    def get_rate(self):
        # print(self.current_user)
        return '4/day'