import requests, sys, os, time, subprocess
from tabulate import tabulate
from tqdm import tqdm

JENKINS_PROJECT = sys.argv[1].split("|")
JENKINS_EXTRA_JOBS = sys.argv[2].split("|")
JENKINS_URL = sys.argv[3]
JENKINS_USERNAME = sys.argv[4]
JENKINS_PASSWORD = sys.argv[5]
SLEEP_TIME = int(sys.argv[6])
SHOW_URLS = int(sys.argv[7]) == 1
TELEGRAM_BOT_TOKEN = sys.argv[8]
TELEGRAM_CHAT_ID = sys.argv[9]
TELEGRAM_MESSAGE = sys.argv[10]
DECORATED_OUTPUT = int(sys.argv[11]) == 1
STOP_ON_NOT_RUNNING = int(sys.argv[12]) == 1
SHOW_PROGRESS_BAR = int(sys.argv[13]) == 1
REQUESTS_TIMEOUT = 10

while "" in JENKINS_EXTRA_JOBS:
    JENKINS_EXTRA_JOBS.remove("")

continueCheck = True
jobStatuses = [None] + list(map(lambda v: None, JENKINS_EXTRA_JOBS))


class bcolors:
    HEADER = "\033[95m" if DECORATED_OUTPUT else ""
    OK = "\033[92m" if DECORATED_OUTPUT else ""
    WARNING = "\033[93m" if DECORATED_OUTPUT else ""
    FAIL = "\033[91m" if DECORATED_OUTPUT else ""
    INFO = "\033[96m" if DECORATED_OUTPUT else ""
    GRAY = "\033[37m" if DECORATED_OUTPUT else ""
    END = "\033[0m" if DECORATED_OUTPUT else ""
    BOLD = "\033[1m" if DECORATED_OUTPUT else ""
    UNDERLINE = "\033[4m" if DECORATED_OUTPUT else ""


def show_error_from_url(url: str):
    print(f"{bcolors.FAIL}Error from url: {bcolors.UNDERLINE}{url}{bcolors.END}")

    if STOP_ON_NOT_RUNNING:
        sys.exit(1)


def do_jenkins_request(url: str):
    try:
        response = requests.get(
            url, auth=(JENKINS_USERNAME, JENKINS_PASSWORD), timeout=REQUESTS_TIMEOUT
        )
        if response.status_code != 200:
            show_error_from_url(url)

        return response
    except:
        show_error_from_url(url)


def get_building_string(build_data: list):
    return (f"{bcolors.WARNING}yes{bcolors.END}") if build_data["building"] else "no"


def get_result(build_data: list, decorated: bool = True):
    if build_data["building"]:
        string = f"{bcolors.WARNING if decorated else ''}BUILDING{bcolors.END if decorated else ''}"
    else:
        string = (
            f'{bcolors.OK if decorated else ""}{build_data["result"]}{bcolors.END if decorated else ""}'
            if build_data["result"] == "SUCCESS"
            else f'{bcolors.FAIL if decorated else ""}{build_data["result"]}{bcolors.END if decorated else ""}'
        )

    return string


def do_telegram_request(text: str):
    if TELEGRAM_BOT_TOKEN == "" or TELEGRAM_CHAT_ID == "":
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    return (
        requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=REQUESTS_TIMEOUT,
        ).status_code
        == 200
    )


def send_notification(status: str = "", job_name: str = ""):
    message = [f'Jenkins for {" > ".join(JENKINS_PROJECT)} is ended']

    if job_name != "":
        message.append(f" {job_name}")

    if status != "":
        message.append(f" with status: {status}")

    message = "".join(message)

    subprocess.Popen(["notify-send", message])
    do_telegram_request(message if TELEGRAM_MESSAGE == "" else TELEGRAM_MESSAGE)


def set_job_statuses(index: int, value: str):
    if jobStatuses[index] != value and jobStatuses[index] == "BUILDING":
        job_name = "Build" if index == 0 else JENKINS_EXTRA_JOBS[index - 1]
        send_notification(value, job_name)

    jobStatuses[index] = value


def console_clear():
    os.system("cls" if os.name == "nt" else "clear")


while continueCheck:
    hasError = False

    try:
        lastBuildUrl = do_jenkins_request(
            f'{JENKINS_URL}/job/{"/job/".join(JENKINS_PROJECT)}/api/json'
        ).json()["lastBuild"]["url"]
        buildData = do_jenkins_request(f"{lastBuildUrl}api/json").json()

        set_job_statuses(0, get_result(buildData, False))

        tableRows = [
            [
                "Build",
                buildData["id"],
                buildData["description"],
                get_building_string(buildData),
                get_result(buildData),
            ]
        ]
        urls = [
            f"{JENKINS_URL}",
            f'{JENKINS_URL}/job/{"/job/".join(JENKINS_PROJECT)}',
            f"{lastBuildUrl}console",
        ]

        extraJobBuildings = []
        for index, extraJob in enumerate(JENKINS_EXTRA_JOBS):
            extraJobBuilding = False
            if extraJob != "":
                try:
                    promotion = do_jenkins_request(
                        f'{JENKINS_URL}/job/{"/job/".join(JENKINS_PROJECT)}/promotion/process/{extraJob}/api/json'
                    ).json()["lastBuild"]
                    promotionData = do_jenkins_request(
                        f'{JENKINS_URL}/job/{"/job/".join(JENKINS_PROJECT)}/promotion/process/{extraJob}/{str(promotion["number"])}/api/json'
                    ).json()

                    set_job_statuses(index + 1, get_result(promotionData, False))

                    urls.append(promotionData["url"])
                    tableRows.append(
                        [
                            f"{bcolors.BOLD}{bcolors.INFO}{extraJob}{bcolors.END}",
                            promotionData["id"],
                            (
                                promotionData["description"]
                                if promotionData["description"]
                                else promotionData["fullDisplayName"]
                            ),
                            get_building_string(promotionData),
                            get_result(promotionData),
                        ]
                    )
                    extraJobBuilding = promotionData["building"]
                except:
                    promotionData = None

            extraJobBuildings.append(extraJobBuilding)

        urls = "\n".join(urls)

        console_clear()

        print(
            f'{bcolors.HEADER}Project:{bcolors.BOLD} {" > ".join(JENKINS_PROJECT)}{bcolors.END}'
        )
        print("")
        print(
            tabulate(
                tableRows,
                headers=[
                    f"{bcolors.BOLD}Operation{bcolors.END}",
                    f"{bcolors.BOLD}ID{bcolors.END}",
                    f"{bcolors.BOLD}Description{bcolors.END}",
                    f"{bcolors.BOLD}Running{bcolors.END}",
                    f"{bcolors.BOLD}Status{bcolors.END}",
                ],
                tablefmt="rounded_grid",
            )
        )

        if SHOW_URLS:
            print("")
            print(f"{bcolors.GRAY}URLs:{bcolors.END}")
            print(f"{bcolors.GRAY}{bcolors.UNDERLINE}{urls}{bcolors.END}")

        print("")

        continueCheck = (
            buildData["building"] or (True in extraJobBuildings) or not STOP_ON_NOT_RUNNING
        )
    except:
        hasError = True

    if continueCheck:
        if SHOW_PROGRESS_BAR:
            print("Reloading")
            for i in tqdm(range(SLEEP_TIME)):
                time.sleep(1)
        else:
            time.sleep(SLEEP_TIME)
        
        if hasError:
            console_clear()
