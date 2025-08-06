from backend import app

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', debug=True)
if __name__ == '__main__':  # Script executed directly?
    print("songs application.")
    app.run(host="0.0.0.0", port=8080, debug=True,use_reloader=True)  # Launch built-in web server and run this Flask webapp
