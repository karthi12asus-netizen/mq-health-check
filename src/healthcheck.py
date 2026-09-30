import os
import sys
import json
import pymqi

QM_NAME = os.getenv("MQ_QMGR", "QM1")
HOST = os.getenv("MQ_HOST", "172.18.0.1")
PORT = int(os.getenv("MQ_PORT", "1414"))
CHANNEL = os.getenv("MQ_CHANNEL", "DEV.APP.SVRCONN")
USERNAME = os.getenv("MQ_USER", "app")
PASSWORD = os.getenv("MQ_PASSWORD", "passw0rd")

WARNING_THRESHOLD = 10

QUEUES = [
    "APP.REQUEST",
    "APP.RESPONSE",
    "APP.ERROR",
]


def main():
    print("=" * 40)
    print("          MQ HEALTH CHECK")
    print("=" * 40)

    print(f"Queue Manager : {QM_NAME}")
    print(f"Host          : {HOST}")
    print(f"Port          : {PORT}")
    print(f"Channel       : {CHANNEL}")
    print()

    qmgr = None
    exit_code = 0

    report = {
        "queue_manager": QM_NAME,
        "host": HOST,
        "port": PORT,
        "status": "HEALTHY",
        "queues": [],
    }

    try:
        print("Connecting to IBM MQ...")

        qmgr = pymqi.connect(
            QM_NAME,
            CHANNEL,
            f"{HOST}({PORT})",
            USERNAME,
            PASSWORD,
        )

        print("Connection    : SUCCESS")
        print()

        print("Queue Status")
        print("-" * 40)

        overall_status = "HEALTHY"

        for queue_name in QUEUES:

            queue = pymqi.Queue(
                qmgr,
                queue_name,
                pymqi.CMQC.MQOO_INQUIRE,
            )

            try:
                depth = queue.inquire(
                    pymqi.CMQC.MQIA_CURRENT_Q_DEPTH
                )

                if depth >= WARNING_THRESHOLD:
                    status = "WARNING"
                    overall_status = "WARNING"
                    exit_code = 1
                else:
                    status = "OK"

                print(
                    f"{queue_name:<15} "
                    f"Depth: {depth:<5} "
                    f"Status: {status}"
                )

                report["queues"].append(
                    {
                        "name": queue_name,
                        "depth": depth,
                        "status": status,
                    }
                )

            finally:
                queue.close()

        report["status"] = overall_status

        print()
        print("-" * 40)
        print(f"Overall Status: {overall_status}")
        print("-" * 40)

        print()
        print("JSON Report")
        print("-" * 40)
        print(json.dumps(report, indent=2))

        os.makedirs("reports", exist_ok=True)

        with open("reports/health-report.json", "w") as report_file:
            json.dump(report, report_file, indent=2)

        print()
        print("Report saved to reports/health-report.json")

    except Exception as error:

        print()
        print("Overall Status: FAILED")
        print(f"Error         : {error}")

        report["status"] = "FAILED"
        report["error"] = str(error)

        os.makedirs("reports", exist_ok=True)

        with open("reports/health-report.json", "w") as report_file:
            json.dump(report, report_file, indent=2)

        exit_code = 2

    finally:

        if qmgr is not None:
            qmgr.disconnect()
            print()
            print("MQ Disconnect : SUCCESS")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
