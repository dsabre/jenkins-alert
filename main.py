import requests, sys, os, time, subprocess;
from tabulate import tabulate

JENKINS_PROJECT = sys.argv[1]
JENKINS_PROMOTION_STAGE_NAME = sys.argv[2]
JENKINS_PROMOTION_PROD_NAME = sys.argv[3]
JENKINS_URL = sys.argv[4]
JENKINS_USERNAME = sys.argv[5]
JENKINS_PASSWORD = sys.argv[6]
SLEEP_TIME = float(sys.argv[7])
TELEGRAM_BOT_TOKEN = sys.argv[8]
TELEGRAM_CHAT_ID = sys.argv[9]
TELEGRAM_MESSAGE = sys.argv[10]
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
    lastBuildUrl = do_jenkins_request(f'{JENKINS_URL}/job/{JENKINS_PROJECT}/api/json').json()['lastBuild']['url']
    buildData = do_jenkins_request(f'{lastBuildUrl}api/json').json()
    promotionStage = do_jenkins_request(f'{JENKINS_URL}/job/{JENKINS_PROJECT}/promotion/process/{JENKINS_PROMOTION_STAGE_NAME}/api/json').json()['lastBuild']
    promotionProd = do_jenkins_request(f'{JENKINS_URL}/job/{JENKINS_PROJECT}/promotion/process/{JENKINS_PROMOTION_PROD_NAME}/api/json').json()['lastBuild']

    tableRows = [['Build', buildData['id'], get_building_string(buildData), get_result(buildData)]]

    promotionStageBuilding = False
    try:
        promotionStageData = do_jenkins_request(f'{JENKINS_URL}/job/{JENKINS_PROJECT}/promotion/process/{JENKINS_PROMOTION_STAGE_NAME}/{str(promotionStage["number"])}/api/json').json()
        tableRows.append([f'Promotion {bcolors.BOLD}{bcolors.INFO}{JENKINS_PROMOTION_STAGE_NAME}{bcolors.END}', promotionStageData['id'], get_building_string(promotionStageData), get_result(promotionStageData)])
        promotionStageBuilding = promotionStageData['building']
    except:
        promotionStageData = None

    promotionProdBuilding = False
    try:
        promotionProdData = do_jenkins_request(f'{JENKINS_URL}/job/{JENKINS_PROJECT}/promotion/process/{JENKINS_PROMOTION_PROD_NAME}/{str(promotionProd["number"])}/api/json').json()
        tableRows.append([f'Promotion {bcolors.BOLD}{bcolors.INFO}{JENKINS_PROMOTION_PROD_NAME}{bcolors.END}', promotionProdData['id'], get_building_string(promotionProdData), get_result(promotionProdData)])
        promotionProdBuilding = promotionProdData['building']
    except:
        promotionProdData = None

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{bcolors.HEADER}Project:{bcolors.BOLD} {JENKINS_PROJECT}{bcolors.END}')
    print('')
    print(f'{bcolors.GRAY}URLs:{bcolors.END}')
    print(f'{bcolors.GRAY}({bcolors.UNDERLINE}{JENKINS_URL}{bcolors.END}{bcolors.GRAY})\n({bcolors.UNDERLINE}{JENKINS_URL}/job/{JENKINS_PROJECT}{bcolors.END}{bcolors.GRAY}){bcolors.END}')
    print('')
    print(tabulate(tableRows, headers=[
        f'{bcolors.BOLD}Operation{bcolors.END}',
        f'{bcolors.BOLD}ID{bcolors.END}',
        f'{bcolors.BOLD}Running{bcolors.END}',
        f'{bcolors.BOLD}Status{bcolors.END}'
        ], tablefmt='rounded_grid'))
    print('')

    continueCheck = buildData['building'] or promotionStageBuilding or promotionProdBuilding

    if continueCheck:
        showNotification = True
        time.sleep(SLEEP_TIME)

if showNotification:
    message = f'Jenkins for {JENKINS_PROJECT} is ended'
    subprocess.Popen(['notify-send', message])
    do_telegram_request(message if TELEGRAM_MESSAGE == '' else TELEGRAM_MESSAGE)