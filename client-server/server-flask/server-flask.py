from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/hello', methods=['POST'])
def hello():
    data = request.json
    name = data.get('name', 'Mundo')
    return jsonify({"message": f"Hola, {name}!"})

if __name__ == '__main__':
    app.run(debug=True)