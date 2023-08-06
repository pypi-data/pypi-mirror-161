import mysql.connector
from mysql.connector import errorcode, pooling
from paketmutfak.utils.functions.general import init_extra_log_params, generate_uid
from paketmutfak.utils.constants.error_codes import MessageCode


class PmMysqlBaseClass:
    def __init__(self, host, port, user, password, database, pool_name, table_name, pm_logger, pool_size=10):

        self.pm_logger = pm_logger

        res = {}
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database

        self.table_name = table_name

        res["host"] = self._host
        res["port"] = self._port
        res["user"] = self._user
        res["password"] = self._password
        res["database"] = self._database
        self.dbconfig = res
        self.pool = self.create_pool(pool_name=pool_name, pool_size=pool_size)

    def create_pool(self, pool_name="mypool", pool_size=3):
        """
        Create db connection pool, after created, the request of connecting
        MySQL could get db connection from this pool instead of request to
        create db connection.
        :param pool_name: the name of pool, default is "mypool"
        :param pool_size: the size of pool, default is 3
        :return: connection pool
        """
        # TODO : Burada poolda hata varsa ne yapılmalı ?
        pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **self.dbconfig)

        return pool

    def close(self):
        self.close()

    @staticmethod
    def close(conn, cursor):
        """
        A method used to close connection of mysql.
        :param conn:
        :param cursor:
        :return:
        """
        cursor.close()
        conn.close()

    def execute(self, sql, args=None, commit=False):
        """
        Execute db sql, it could be with args and with out args. The usage is
        similar with execute() function in module pymysql.
        :param sql: sql clause
        :param args: args need by sql clause
        :param commit: whether to commit
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            if args:
                cursor.execute(sql, args)
            else:
                cursor.execute(sql)
            if commit is True:
                conn.commit()
                row_count = cursor.rowcount
                self.close(conn, cursor)
                return row_count
            else:
                res = cursor.fetchall()
                self.close(conn, cursor)
                return res
        except mysql.connector.PoolError as poolErr:
            if conn:
                self.close(conn, cursor)
            log_id = generate_uid()
            self.pm_logger.error(msg=f"get_connection error: {poolErr}",
                                 extra=init_extra_log_params(log_id=log_id,
                                                             table_name=self.table_name,
                                                             db_name=self._database))
            return {"log_id": log_id, "status": "BAD", "status_code": "BAD"}
        except mysql.connector.Error as err:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=err, sql_statement=sql)
            return respond
        except Exception as exp:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=exp, sql_statement=sql)
            return respond

    def executemany(self, sql, args, commit=False):
        """
        Execute with many args. Similar with executemany() function in pymysql.
        args should be db sequence.
        :param sql: sql clause
        :param args: args
        :param commit: commit or not.
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.executemany(sql, args)
            if commit is True:
                conn.commit()
                row_count = cursor.rowcount
                self.close(conn, cursor)
                return row_count
            else:
                res = cursor.fetchall()
                self.close(conn, cursor)
                return res
        except mysql.connector.PoolError as poolErr:
            if conn:
                self.close(conn, cursor)
            log_id = generate_uid()
            self.pm_logger.error(msg=f"get_connection error: {poolErr}",
                                 extra=init_extra_log_params(log_id=log_id,
                                                             table_name=self.table_name,
                                                             db_name=self._database))
            return {"log_id": log_id, "status": "BAD", "status_code": "BAD"}
        except mysql.connector.Error as err:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=err, sql_statement=sql)
            return respond
        except Exception as exp:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=exp, sql_statement=sql)
            return respond

    def get_connection_conn_cursor(self):
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
        except mysql.connector.Error as err:
            respond = self.database_error_handling_to_log(error=err, sql_statement="Connection Pool Error")
            return respond, None
        except Exception as exp:
            respond = self.database_error_handling_to_log(error=exp, sql_statement="Connection Pool Error")
            return respond, None
        else:
            return conn, cursor

    def executemany_without_commit(self, conn, cursor, sql, args):
        try:
            cursor.executemany(sql, args)
            row_count = cursor.rowcount
        except mysql.connector.PoolError as poolErr:
            if conn:
                self.close(conn, cursor)
            log_id = generate_uid()
            self.pm_logger.error(msg=f"get_connection error: {poolErr}",
                                 extra=init_extra_log_params(log_id=log_id,
                                                             table_name=self.table_name,
                                                             db_name=self._database))
            return {"log_id": log_id, "status": "BAD", "status_code": "BAD"}
        except mysql.connector.Error as err:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=err, sql_statement=sql)
            return respond
        except Exception as exp:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=exp, sql_statement=sql)
            return respond
        else:
            return row_count

    def execute_without_commit(self, conn, cursor, sql, args=None):
        try:
            if args:
                cursor.execute(sql, args)
            else:
                cursor.execute(sql)

            row_count = cursor.rowcount
        except mysql.connector.PoolError as poolErr:
            if conn:
                self.close(conn, cursor)
            log_id = generate_uid()
            self.pm_logger.error(msg=f"get_connection error: {poolErr}",
                                 extra=init_extra_log_params(log_id=log_id,
                                                             table_name=self.table_name,
                                                             db_name=self._database))
            return {"log_id": log_id, "status": "BAD", "status_code": "BAD"}
        except mysql.connector.Error as err:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=err, sql_statement=sql)
            return respond
        except Exception as exp:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=exp, sql_statement=sql)
            return respond
        else:
            return row_count

    def commit_without_execute(self, conn, cursor):
        try:
            conn.commit()
            if conn:
                self.close(conn, cursor)

            row_count = cursor.rowcount
        except mysql.connector.PoolError as poolErr:
            if conn:
                self.close(conn, cursor)
            log_id = generate_uid()
            self.pm_logger.error(msg=f"get_connection error: {poolErr}",
                                 extra=init_extra_log_params(log_id=log_id,
                                                             table_name=self.table_name,
                                                             db_name=self._database))
            return {"log_id": log_id, "status": "BAD", "status_code": "BAD"}
        except mysql.connector.Error as err:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=err, sql_statement="")
            return respond
        except Exception as exp:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=exp, sql_statement="")
            return respond
        else:
            return row_count

    def callprocedure(self, proc_name, args_array, commit=True):
        """
        :param commit:
        :param proc_name: procedure name
        :param args_array: args
        :return: if commit, return None, else, return result
        """
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()

            cursor.callproc(proc_name, args_array)
            if commit is False:  # TODO: Procedureden veri çekme durumu ile ilgili test yapılmalı
                for result in cursor.stored_results():
                    print("++", result.fetchall())
            elif commit is True:
                for result in cursor.stored_results():  # Hata mesajı
                    return {"status_code": "BAD", "error_message": result.fetchall()[0]}
        except mysql.connector.PoolError as poolErr:
            if conn:
                self.close(conn, cursor)
            log_id = generate_uid()
            self.pm_logger.error(msg=f"get_connection error: {poolErr}",
                                 extra=init_extra_log_params(log_id=log_id,
                                                             table_name=self.table_name,
                                                             db_name=self._database))
            return {"log_id": log_id, "status": "BAD", "status_code": "BAD"}
        except mysql.connector.Error as err:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=err, sql_statement=proc_name)
            return respond
        except Exception as exp:
            if conn:
                self.close(conn, cursor)
            respond = self.database_error_handling_to_log(error=exp, sql_statement=proc_name)
            return respond
        else:
            return
        finally:
            if conn.is_connected():
                self.close(conn, cursor)

    def database_error_handling_to_log(self, error, sql_statement):
        pm_db_errno = -1
        if "errno" in error.__dict__:
            pm_db_errno = error.errno
            if error.errno == errorcode.ER_BAD_TABLE_ERROR:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement}
            elif error.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement}
            elif error.errno == errorcode.ER_PARSE_ERROR:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement}
            elif error.errno == errorcode.ER_BAD_FIELD_ERROR:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement}
            elif error.errno == errorcode.ER_WRONG_FIELD_WITH_GROUP:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement}
            elif error.errno == errorcode.ER_DUP_FIELDNAME:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement}
            elif error.errno == errorcode.ER_DUP_KEYNAME:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement}
            elif error.errno == errorcode.ER_NO_SUCH_TABLE:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement}
            else:
                log_message = {'status': 'BAD',
                               'error_message': f"Error '{self.table_name}': {error}",
                               'sql_statement': sql_statement,
                               'errno': error.errno}
        else:
            log_message = {'status': 'BAD', 'error_message': f"Something went wrong on '{self.table_name}': "}

        log_id = generate_uid()
        self.pm_logger.error(msg=log_message.get("error_message"),
                             extra=init_extra_log_params(log_id=log_id,
                                                         table_name=self.table_name,
                                                         sql_statement=sql_statement,
                                                         db_name=self._database,
                                                         sql_error_code=pm_db_errno,
                                                         error_code=MessageCode.UNEXPECTED_ERROR_ON_SERVICE_MESSAGE))

        return {"log_id": log_id,
                "status_code": "BAD",
                "sql_error_code": pm_db_errno,
                "error_message": log_message.get("error_message")}
