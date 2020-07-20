import datetime

class PuzzleCounter():

    def __init__(self):
        # with open('counter.txt', 'r+', encoding="utf-8-sig") as f:
        with open('/home/vojtech/web.kotek.co/myapp/counter.txt', 'r+', encoding="utf-8-sig") as f:
            self.errors = []
            self.counter = f.readlines()
            self.count = self.count()
            self.sessions = self.sessions()
            self.last = self.sessions[-1]
            self.state = self.state() # (state, time started (unix), time started (nice))
            self.time
        pass

    def add(self, action):
        if action not in ('STA','END','ADD'):
            print("ERROR! Wrong action:", action)
        pass

    def count(self):

        # Get total count
        count = 0
        for line in self.counter:
            if 'ADD' in line:
                count += 1

        return count
    
    def elapsed_seconds(self):
        seconds = 0
        return [seconds+x['DURATION'] for x in self.sessions]

    def sessions(self):

        sessions = []

        for n, line in enumerate(self.counter):

            try:
                action, timestamp = line.split(';')

                if action == "STA":
                    session = {
                        "START": round(float(timestamp.strip())),
                        "PIECES": 0,
                    }
                elif action == "ADD":
                    session['PIECES'] += 1
                elif action == "END":
                    session["END"] = round(float(timestamp.strip()))
                    session["DURATION"] = session["END"] - session["START"]
                    session["START"] = datetime.datetime.fromtimestamp(session["START"]).strftime("%Y-%m-%d %H:%M:%S")
                    session["END"] = datetime.datetime.fromtimestamp(session["END"]).strftime("%Y-%m-%d %H:%M:%S")
                    sessions += [session]
            except Exception as e:
                error = "ERROR: {}\nLINE: {}\nVALUE: {}".format(e, n, line)
                self.errors += [error]
                print(error)

        return sessions

    def state(self):

        lines = self.counter
        lines.reverse()

        # Get last start/end date
        for line in lines:
            state = line.strip().split(";")
            if state[0] in ['STA', 'END']:
                break

            time = float( state[1] )
            time_nice = datetime.datetime.fromtimestamp(time).strftime("%H:%M:%S")

        return (state[0], time, time_nice)

    def stats(self):
        
        def duration(seconds):
            return {
                'days': int( seconds // (60*60*24) ),
                'hours': int( ( seconds % (60*60*24) ) // (60*60) ),
                'minutes': int( ( seconds % (60*60) ) // (60) ),
                'seconds': int( seconds % (60*60) ),
            }

        self.rate = int(total_seconds / count)
        self.remaining_seconds = ( 9000 - count ) * self.rate
        self.remaining_time = duration(self.remaining_seconds)
        self.elapsed_seconds = [
       

        return {
            'total_seconds': duration(total_seconds),
            'time_pretty': time_nice,
        }
