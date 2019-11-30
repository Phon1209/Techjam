import operator
import re
from http import HTTPStatus
import math

from flask import Flask, jsonify, request

app = Flask(__name__)

variable_re = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
robot_re = re.compile(r"^robotF([1-9][0-9]*)$")
func_map = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
}

variables = {}

def isPosition(pos):
    if isinstance(pos['x'], int) and isinstance(pos['y'],int) : return True
    else : return False


@app.route("/distance", methods=['POST'])
def distance():
    body = request.get_json()
    first = body['first_pos']
    second = body['second_pos']
    if not isPosition(first) and not isinstance(first,str) : 
        return HTTPStatus.BAD_REQUEST 
    if not isPosition(second) and not isinstance(second,str) : 
        return HTTPStatus.BAD_REQUEST 

    if "robot#" in first : 
        first= _get_position(first)
    if "robot#" in second :
        second = _get_position(second)

    if first == None || second == None : 
        return HTTPStatus.FAILED_DEPENDENCY
    
    
    if body['metric'] == 'manhattan':
        result = calculate_distance(first,second,True)
    else :
        result = calculate_distance(first,second,False)
    return jsonify(result=result), HTTPStatus.OK

def calculate_distance(first,second,man):
    delta_x = first['x']-second['x']
    delta_y = first['y'] - second['y']
    if man : 
        value = delta_x + delta_y
    else : 
        value = math.pow((delta_x*delta_x + delta_y*delta_y),0.5)
    return value



def _get_position(token):
    if robot_re.fullmatch(token):
        p = token.split("#")
        value = get_robot_position(p[-1])
    else :
        value = token
    return value


def _get_value(token):
    if variable_re.fullmatch(token):
        value = variables[token]
    else:
        value = token
    return float(value)

# /robot/{robot_id}/position
@app.route("/robot/<robot_id>/position", methods=['PUT'])
def put_variable(robot_id):
    body = request.get_json()
    if robot_id not in range(1..999999):
        return HTTPStatus.BAD_REQUEST
    variables[name] = body['position']
    return '', HTTPStatus.NO_CONTENT


@app.route("/robot/<robot_id>/position", methods=['GET'])
def get_variable(robot_id):
    if robot_id not in variables:
        return '', HTTPStatus.NOT_FOUND
    else :
        value = variables[robot_id]
        return HTTPStatus.OK,jsonify(value=value) 

def get_robot_position(robot_id):

    if robot_id in variables:
        return variables[robot_id]
    else : 
        return None

@app.route("/nearest", methods=['POST'])
def get_nearest():
    body = request.get_json()
    if not isPosition(body['ref_position']):
        return HTTPStatus.BAD_REQUEST
    if body['k'] == None:
        k = 1
    else:
        if not isinstance(body['k'],int):
            return HTTPStatus.BAD_REQUEST
        else k = body['k']
    
    value = []
    reference = body['ref_position']
    a = []
    for key in variables:
        d = calculate_distance(reference,variables[key],False)
        a.append((d,key))
    
    a.sort()
    for i in a:
        value.append(i[0])
        k -= 1
        if k==0 :
            break
    return value,HTTPStatus.OK