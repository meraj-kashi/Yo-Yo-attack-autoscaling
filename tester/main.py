import requests, datetime, csv
from apscheduler.schedulers.background import BackgroundScheduler as scheduler

def send_request():
    url = 'http://router'
    try:
        request = requests.get(url)
    except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as err:
        print("Error while trying to POST pid data")
        print(err)
    finally:
        request.close()

    status_code = request.status_code
    response_time = request.elapsed.total_seconds()
    interval = datetime.datetime.now()
    result = str(status_code) +","+ str(response_time)+","+ str(interval)

    print(result)

    with open('countries.csv', 'a+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f,delimiter=',')
        writer.writerows([str(status_code), str(response_time) , str(interval)])
        f.close()


    return request.content

sch = scheduler()
sch.add_job(send_request, 'interval', seconds=2)
sch.start()

# This code will be executed after the sceduler has started
try:
    print('Scheduler started, ctrl-c to exit!')
    while 1:
        # Notice here that if you use "pass" you create an unthrottled loop
        # try uncommenting "pass" vs "input()" and watching your cpu usage.
        # Another alternative would be to use a short sleep: time.sleep(.1)

        pass
        #input()
except KeyboardInterrupt:
    if sch.state:
        sch.shutdown()