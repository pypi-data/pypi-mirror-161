import time as tm


class Timer:
    def timer_point(self, time, repeat = False):
        ''' time in seconds
            This function start timer '''
        self.time = time
        self.repeat = repeat
        self.time1 = tm.time()
        self.count = 0

    def check_timer(self):
        ''' This function check
            Was timer fished '''
        time2 = tm.time()
        if time2 < self.time1 + self.time:
            return False
        else:
            if self.repeat:
                self.restart()
                return True
            else:
                if self.count == 0:
                    self.count += 1
                    return True
                return False
        
    def check_time(self):
        ''' This function check
            How much time is left '''
        time2 = tm.time()
        check_time = (self.time1 + self.time) - time2 + 1
        array = [int(check_time // 60), int(check_time % 60)]

        if array[0] < 0 or array[1] < 0:
            return [0, 0]
        else:
            return array
    
    def restart(self):
        ''' This function restart timer '''
        self.timer_point(self.time, self.repeat)
