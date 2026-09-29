import os
import sys
import pymqi

QM_NAME = "QM1"
CHANNEL = "DEV.APP.SVRCONN"

HOST = os.getenv("MQ_HOST", "172.18.0.1")
PORT = int(os.getenv("MQ_PORT", "1414"))

USERNAME = "app"
PASSWORD = "MQhealth123"

QUEUES = [
    "APP.REQUEST",
    "APP.RESPONSE",
    "APP.ERROR",
]

WARNING_THRESHOLD = 10


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

        overall_status = "HEALTHY"

        print("Queue Status")
        print("-" * 40)

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

            finally:
                queue.close()

        print()
        print("-" * 40)
        print(f"Overall Status: {overall_status}")
        print("-" * 40)

    except Exception as error:
        print()
        print("Overall Status: FAILED")
        print(f"Error         : {error}")
        exit_code = 2

    finally:
        if qmgr is not None:
            qmgr.disconnect()
            print("MQ Disconnect : SUCCESS")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
