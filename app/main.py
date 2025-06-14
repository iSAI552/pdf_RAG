from server import app


def main():
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port='8000', log_level="info")


if __name__ == "__main__":
    main()
