from flask import jsonify, make_response
from sqlalchemy import func

class Methods:
    @staticmethod
    def convertToJsonSQLAlchemy(result):
        rv = result.fetchall()
        row_headers = result.keys()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return json_data

    @staticmethod
    def convertFromCursorToSQLAlchemy(proc_name, proc_params, connection = None):
        conn = connection
        if not (conn):
            default_db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            engine = create_engine(default_db_uri)
            conn = engine.raw_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc(proc_name, proc_params)
            columns = [column[0] for column in cursor.description]
            rv = cursor.fetchall()
            json_data = []
            for cursor in rv:
                json_data.append(dict(zip(columns, cursor)))
            conn.commit()
            conn.close()
            return json_data
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def jsonResponseDefinition(object, message, code):
        """
        Takes an Object as parameter to convert it to a Json
        Returns a Response composed by a JSON and an Status Message
        """
        return make_response(jsonify({'data': object, 'message': message, 'status': True}), code)

    @staticmethod
    def jsonResponseDefinitioMessage(message, code):
        """
        Returns a Response composed by a JSON and an Status Message
        """
        return make_response(jsonify({'message': message, 'status': True}), code)

    @staticmethod
    def jsonResponseDefinitionTotal(object, message, code, total):
        """
        Takes an Object as parameter to convert it to a Json
        Returns a Response composed by a JSON and an Status Message
        """
        return make_response(jsonify({'data': object, 'message': message, 'total':total, 'status': True}), code)

    @staticmethod
    def identity_error_response(object, message, is_domain, code):
        """
        Takes an Object as parameter to convert it to a Json
        Returns a Response composed by a JSON and an Status Message
        """
        return make_response(jsonify({'id': 0, 'message': message, 'status':0, 'success':False, 'is_domain':is_domain}), code)

    @staticmethod
    def unexpected_error(error):
        if "(pymysql.err.OperationalError)" in error:
            error = "Can't Connect with the Database, please try again later."
        return make_response(jsonify({'message': 'Unexpected Error: ' + error, 'status': False}), 200)

    @staticmethod
    def wrong_data():
        return make_response(jsonify({'message': 'wrong parameters', 'status': False}), 400)

    @staticmethod
    def not_found():
        return make_response(jsonify({'message': 'not found', 'status': False}), 404)

    #obj : the name of the object you didnt find
    @staticmethod
    def not_found(obj):
        return make_response(jsonify({'message': obj +' not found', 'status': False}), 404)


    @staticmethod
    def generic_error_response(message, code):
        if "(pymysql.err.OperationalError)" in message:
            message = "Can't Connect with the Database, please try again later."
        return make_response(jsonify({'message': message, 'status': False}), code)

    @staticmethod
    def generic_ok_response(message):
        return make_response(jsonify({'message':message, 'status': True}), 200)

    #Count method for the total used for the list queries
    @staticmethod
    def get_count(q):
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

    @staticmethod
    def non_empty_int(v):
        if not v:
            v = None
        else:
            try:
                v = int(v)    
            except Exception as e:
                return Methods.generic_error_response("The param you sent requires to be a number",404)
        return v

    @staticmethod
    def day_of_month(nombre):
        month_number = 0
        if nombre == 'ENERO':
            month_number = 1
        elif nombre == 'FEBRERO':
            month_number = 2
        elif nombre == 'MARZO':
            month_number = 3
        elif nombre == 'ABRIL':
            month_number = 4
        elif nombre == 'MAYO':
            month_number = 5
        elif nombre == 'JUNIO':
            month_number = 6
        elif nombre == 'JULIO':
            month_number = 7
        elif nombre == 'AGOSTO':
            month_number = 8
        elif nombre == 'SEPTIEMBRE':
            month_number = 9
        elif nombre == 'OCTUBRE':
            month_number = 10
        elif nombre == 'NOVIEMBRE':
            month_number = 11
        elif nombre == 'DICIEMBRE':
            month_number = 12

        return month_number
