import requests, sys, os, time, subprocess;
from tabulate import tabulate

JENKINS_PROJECT = sys.argv[1].split("|")
JENKINS_EXTRA_JOBS = sys.argv[2].split("|")
JENKINS_URL = sys.argv[3]
JENKINS_USERNAME = sys.argv[4]
JENKINS_PASSWORD = sys.argv[5]
SLEEP_TIME = float(sys.argv[6])
TELEGRAM_BOT_TOKEN = sys.argv[7]
TELEGRAM_CHAT_ID = sys.argv[8]
TELEGRAM_MESSAGE = sys.argv[9]
REQUESTS_TIMEOUT=10

continueCheck = True
showNotification = False

class bcolors:
    HEADER = '\033[95m'
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    INFO = '\033[96m'
    GRAY = '\033[37m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def show_error_from_url(url):
    print(f"{bcolors.FAIL}Error from url: {bcolors.UNDERLINE}{url}{bcolors.END}")
    sys.exit(1)

def do_jenkins_request(url):
    try:
        response = requests.get(url, auth=(JENKINS_USERNAME, JENKINS_PASSWORD), timeout=REQUESTS_TIMEOUT)
        if response.status_code != 200:
            show_error_from_url(url)
        
        return response
    except:
        show_error_from_url(url)

def get_building_string(build_data):
    return (f'{bcolors.WARNING}yes{bcolors.END}') if build_data['building'] else 'no'

def get_result(build_data):
    if build_data['building']:
        return f'{bcolors.WARNING}BUILDING{bcolors.END}'
    
    return (f'{bcolors.OK}{build_data["result"]}{bcolors.END}' if build_data['result'] == 'SUCCESS' else f'{bcolors.FAIL}{build_data["result"]}{bcolors.END}')

def do_telegram_request(text):
    if TELEGRAM_BOT_TOKEN == '' or TELEGRAM_CHAT_ID == '':
        return False

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    return requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': text}, timeout=REQUESTS_TIMEOUT).status_code == 200

while continueCheck:
    lastBuildUrl = do_jenkins_request(f'{JENKINS_URL}/job/{"/job/".join(JENKINS_PROJECT)}/api/json').json()['lastBuild']['url']
    buildData = do_jenkins_request(f'{lastBuildUrl}api/json').json()
    
    tableRows = [['Build', buildData['id'], get_building_string(buildData), get_result(buildData)]]

    extraJobBuildings = []
    for extraJob in JENKINS_EXTRA_JOBS:
        extraJobBuilding = False
        if extraJob != '':
            try:
                promotion = do_jenkins_request(f'{JENKINS_URL}/job/{"/job/".join(JENKINS_PROJECT)}/promotion/process/{extraJob}/api/json').json()['lastBuild']
                promotionData = do_jenkins_request(f'{JENKINS_URL}/job/{"/job/".join(JENKINS_PROJECT)}/promotion/process/{extraJob}/{str(promotion["number"])}/api/json').json()
                tableRows.append([f'{bcolors.BOLD}{bcolors.INFO}{extraJob}{bcolors.END}', promotionData['id'], get_building_string(promotionData), get_result(promotionData)])
                extraJobBuilding = promotionData['building']
            except:
                promotionData = None
        
        extraJobBuildings.append(extraJobBuilding)

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{bcolors.HEADER}Project:{bcolors.BOLD} {" > ".join(JENKINS_PROJECT)}{bcolors.END}')
    print('')
    print(f'{bcolors.GRAY}URLs:{bcolors.END}')
    print(f'{bcolors.GRAY}({bcolors.UNDERLINE}{JENKINS_URL}{bcolors.END}{bcolors.GRAY})\n({bcolors.UNDERLINE}{JENKINS_URL}/job/{"/job/".join(JENKINS_PROJECT)}{bcolors.END}{bcolors.GRAY}){bcolors.END}')
    print('')
    print(tabulate(tableRows, headers=[
        f'{bcolors.BOLD}Operation{bcolors.END}',
        f'{bcolors.BOLD}ID{bcolors.END}',
        f'{bcolors.BOLD}Running{bcolors.END}',
        f'{bcolors.BOLD}Status{bcolors.END}'
        ], tablefmt='rounded_grid'))
    print('')

    continueCheck = buildData['building'] or (True in extraJobBuildings)

    if continueCheck:
        showNotification = True
        time.sleep(SLEEP_TIME)

if showNotification:
    message = f'Jenkins for {" > ".join(JENKINS_PROJECT)} is ended'
    subprocess.Popen(['notify-send', message])
    do_telegram_request(message if TELEGRAM_MESSAGE == '' else TELEGRAM_MESSAGE)