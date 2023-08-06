import pandas as pd
from datetime import datetime

# PASO SOLO CONEXION Y DATAFRAME A LA CLASE
# PASO LOS DATOS NECESARIOS A CADA MÉTODO

class Transactions:
    def __init__(self, connection, dataframe):
        self.conn = connection
        self.df = dataframe
      
    # DEFINIMOS LA FUNCIÓN
    def delete (self, **kwargs_delete):#aw_sales_order_id, end_date):
        cur = self.conn.cursor()
        self.aw_sales_order_id = kwargs_delete['aw_sales_order_id']
        self.end_date = kwargs_delete['end_date']
        
        # INSERTAMOS EN LA BASE DE DATOS DE SQL
        sentencia = f"""
            DECLARE @Existeaw_sales_order_id int
            DECLARE @salida int
            EXEC uspdAdventureWorksSalesOrders1_1 {self.aw_sales_order_id}, \'{self.end_date}\', @salida OUTPUT
            SELECT @salida
            """
        cur.execute(sentencia)
        salida = cur.fetchall()[0][0]
        
        # PREGUNTA DE CONFIRMACIÓN DE CAMBIOS
        if salida==0:
            print(f'The order with AWSalesOrders:{self.aw_sales_order_id} is deleted on date: {self.end_date}')
            confirm = 'yes'#input('Want to confirm the changes? yes/no: ')
            
            if confirm == 'yes':
                # GUARDAMOS LOS CAMBIOS HECHOS EN SQL
                self.conn.commit()
                # INSERTAMOS EN LA ESTRUCTURA DE PYTHON
                index = self.df['AWSalesOrderID'] == self.aw_sales_order_id
                self.df.loc[index, 'EndDate'] = self.end_date
                print('Table updated correctly')
                
            else:
                # DESHACEMOS LOS CAMBIOS HECHOS EN SQL
                self.conn.rollback()
                print('Table not updated')
        else:
            print(f'The value given for aw_sales_order_id: {self.aw_sales_order_id} does not exist')
            self.conn.rollback()
            print('Error, Table not updated')
            
            
    def insert(self, **kwargs_insert):#customer_id, product_id, order_date, ship_date, order_qty, unit_price, end_date):
        self.customer_id = kwargs_insert['customer_id']
        self.product_id = kwargs_insert['product_id']
        self.order_date = kwargs_insert['order_date']
        self.ship_date = kwargs_insert['ship_date']
        self.order_qty = kwargs_insert['order_qty']
        self.unit_price = kwargs_insert['unit_price']
        self.end_date = kwargs_insert['end_date']
        
        #Insertar una fila en la tabla del SQL:
        query1 = f'DECLARE @Status int = 0; \
                EXEC @Status = M2CML22.dbo.uspiAdventureWorksSalesOrders\
                {self.customer_id}, {self.product_id}, \'{self.order_date}\', \'{self.ship_date}\',\
                {self.order_qty}, {self.unit_price}, \'{self.end_date}\';\
                SELECT @Status'
        cur = self.conn.cursor()
        cur.execute(query1)
        status = cur.fetchone()[0]
        cur.close()
        #--------------------------------------------------------------------------
        #Importar la fila insertada:
        if status == 0:
            print('Fila insertada correctamente.')
            query2 = 'SELECT TOP 1 * FROM M2CML22.dbo.AdventureWorksSalesOrders\
                            				ORDER BY AWSalesOrderID DESC'
            df_aux = pd.read_sql(query2, self.conn, parse_dates = ['OrderDate','ShipDate','EndDate']) 
            #Añadimos el DateStart:
            df_aux.insert(12, "DateStart", datetime.now()) 
            #Insertamos la fila en el DatFrame:
            self.df.loc[len(self.df)] = df_aux.iloc[0] 
            self.conn.commit()
        #--------------------------------------------------------------------------
        #Reporte de errores:
        elif status == -1:
            print('El CustomerID introducido no existe.')
        elif status == -2:
            print('El ProductID introducido no existe.'	)
        elif status == -3:
            print('La fecha de envío debe ser posterior a la fecha de orden')







