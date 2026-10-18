from verity import create_app

app = create_app()


if __name__ == "__main__":
    app.logger.info("Starting Verity media analysis app")
    app.run(debug=app.config["DEBUG"])
