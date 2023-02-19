# p2app/engine/main.py
#
# ICS 33 Winter 2023
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.
from p2app.events import *
from p2app.events.database import *
import sqlite3

def getdb_(db_name):
    # Connect to database (if it doesn't exist, it will be created)
    conn = sqlite3.connect(db_name)

    # Create a cursor to execute SQL statements
    c = conn.cursor()

    try:
        yield conn, c
    finally:
        conn.close()
import sqlite3

def getdb(db_name, query,param = None):
    # Connect to database (if it doesn't exist, it will be created)
    conn = sqlite3.connect(db_name)
    # Create a cursor to execute SQL statements
    c = conn.cursor()
    # Execute the query and get the results
    c.execute(query,(param))
    results = c.fetchall()
    # Close connection
    conn.commit()
    conn.close()
    # Return the results
    return results



class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self.database_name = None



    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        if isinstance(event,OpenDatabaseEvent):
            self.database_name = event._path
            getdb_(self.database_name)
            yield from [DatabaseOpenedEvent(event._path)] # else DatabaseOpenFailedEvent if fails
        elif isinstance(event,QuitInitiatedEvent):
            yield EndApplicationEvent
        elif isinstance(event,CloseDatabaseEvent):
            yield DatabaseClosedEvent
################continent related event###############################
        elif isinstance(event,StartContinentSearchEvent):
            results = self.fetch_query_continent(event)
            # Print the results
            for row in results:
                yield ContinentSearchResultEvent(Continent(*row))
            # from p2app.events.continents import Continent
             #for each one found else empty
        elif isinstance(event,LoadContinentEvent):
            results = self.fetch_query_continent(event)
            yield ContinentLoadedEvent(Continent(*results[0]))
        elif isinstance(event,SaveNewContinentEvent):
            try:
                self.insert_query(event)
                yield ContinentSavedEvent(event.continent())
            except sqlite3.IntegrityError as exe:
                yield SaveContinentFailedEvent("Failed to Add new Continent due to duplicates")
        elif isinstance(event,SaveContinentEvent):
            try:
                result = self.update_query(event)
                yield ContinentSavedEvent(event.continent())
            except:
                yield SaveContinentFailedEvent("Updating the Database has failed")

############Country-related events######################
        elif isinstance(event,StartCountrySearchEvent):
            results = self.fetch_query_continent(event)
            yield CountrySearchResultEvent()   #One CountrySearchResultEvent for each country found in the search.
                                            # If no countries were found, no events are returned.
        elif isinstance(event,LoadCountryEvent):
            yield CountryLoadedEvent
        elif isinstance(event,SaveNewCountryEvent):
            yield CountrySavedEvent    #If saving the country failed, SaveCountryFailedEvent
                                        # with a user-friendly error message.
        elif isinstance(event,SaveCountryEvent):
            yield CountrySavedEvent    #If saving the country failed,
                                        # SaveCountryFailedEvent with a user-friendly error message.


#################Region-related events################
        elif isinstance(event,StartRegionSearchEvent):
            yield RegionSearchResultEvent
        elif isinstance(event,LoadRegionEvent):
            yield RegionLoadedEvent
        elif isinstance(event,SaveNewRegionEvent):
            yield RegionSavedEvent    #If saving the country failed, SaveRegionFailedEvent
                                        # with a user-friendly error message.
        elif isinstance(event,SaveRegionEvent):
            yield RegionSavedEvent    #If saving the country failed,
                                        # SaveRegionFailedEvent with a user-friendly error message.
        else:ErrorEvent
        yield from ()


#######################  helper functions for Continent#################
    def fetch_query(self, event):
        # Define the query
        query = 'SELECT * FROM continent c WHERE 1=1'

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed

        query,param_tuple = self.query_formater(event, query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def insert_query(self, event):
        # Define the query
        query = "INSERT INTO continent"

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed

        query,param_tuple = self.insert_query_formater(event.continent(), query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def update_query(self, event):
        # Define the query
        query = 'UPDATE continent SET'

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed
        query,param_tuple = self.update_query_formater(event.continent(), query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def insert_query_formater(self, event, query):
        values = []
        columns = []
        params = []
        if "continent_code" in event.__dir__() and not callable(event.continent_code):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("continent_code")
            params.append(event.continent_code)
        if "name" in event.__dir__() and not callable(event.name):
            # query += " name = ?"
            values.append("?")
            columns.append("name")
            params.append(event.name)

        columns_str = ", ".join(columns)
        values_str = ", ".join(values)

        # Append the column names and placeholders to the query string
        query += f"({columns_str}) VALUES ({values_str})"

        return query,params

    def update_query_formater(self, event, query):
        param_tuple = []
        if "continent_code" in event.__dir__() and not callable(event.continent_code):
            query += " continent_code = ?,"
            param_tuple.append(event.continent_code)
        if "name" in event.__dir__() and not callable(event.name):
            query += " name = ?,"
            param_tuple.append(event.name)
        query = query.rstrip(',')
        if "continent_id" in event.__dir__() and not callable(event.continent_id):
            query += " where continent_id = ?"
            param_tuple.append(event.continent_id)

        return query,param_tuple

    def query_formater(self, event, query):
        param_tuple = []
        if "continent_code" in event.__dir__() and event.continent_code():
            query += " AND continent_code LIKE ?"
            continent_code = '%' + event.continent_code() + '%'
            param_tuple.append(continent_code)
        if "name" in event.__dir__() and event.name():
            query += " AND name LIKE ?"
            name = '%' + event.name() + '%'
            param_tuple.append(name)
        if "continent_id" in event.__dir__() and event.continent_id():
            query += " AND continent_id = ?"
            continent_code = event.continent_id()
            param_tuple.append(continent_code)

            # Call the getdb function with the query
        return query,param_tuple

#######################  helper functions for Continent#################

    def fetch_query_continent(self, event):
        # Define the query
        query = 'SELECT * FROM continent c WHERE 1=1'

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed

        query,param_tuple = self.query_formater(event, query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def insert_query(self, event):
        # Define the query
        query = "INSERT INTO continent"

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed

        query,param_tuple = self.insert_query_formater(event.continent(), query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def update_query(self, event):
        # Define the query
        query = 'UPDATE continent SET'

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed
        query,param_tuple = self.update_query_formater(event.continent(), query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def insert_query_formater(self, event, query):
        values = []
        columns = []
        params = []
        if "continent_code" in event.__dir__() and not callable(event.continent_code):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("continent_code")
            params.append(event.continent_code)
        if "name" in event.__dir__() and not callable(event.name):
            # query += " name = ?"
            values.append("?")
            columns.append("name")
            params.append(event.name)

        columns_str = ", ".join(columns)
        values_str = ", ".join(values)

        # Append the column names and placeholders to the query string
        query += f"({columns_str}) VALUES ({values_str})"

        return query,params

    def update_query_formater(self, event, query):
        param_tuple = []
        if "continent_code" in event.__dir__() and not callable(event.continent_code):
            query += " continent_code = ?,"
            param_tuple.append(event.continent_code)
        if "name" in event.__dir__() and not callable(event.name):
            query += " name = ?,"
            param_tuple.append(event.name)
        query = query.rstrip(',')
        if "continent_id" in event.__dir__() and not callable(event.continent_id):
            query += " where continent_id = ?"
            param_tuple.append(event.continent_id)

        return query,param_tuple

    def query_formater(self, event, query):
        param_tuple = []
        if "continent_code" in event.__dir__() and event.continent_code():
            query += " AND continent_code LIKE ?"
            continent_code = '%' + event.continent_code() + '%'
            param_tuple.append(continent_code)
        if "name" in event.__dir__() and event.name():
            query += " AND name LIKE ?"
            name = '%' + event.name() + '%'
            param_tuple.append(name)
        if "continent_id" in event.__dir__() and event.continent_id():
            query += " AND continent_id = ?"
            continent_code = event.continent_id()
            param_tuple.append(continent_code)

            # Call the getdb function with the query
        return query,param_tuple
# with getdb('airport.db') as (conn, c):
#
#     # Insert data into the table
#     c.execute("INSERT INTO example_table VALUES (1, 'John', 25)")
#     c.execute("INSERT INTO example_table VALUES (2, 'Jane', 30)")
#
#     # Commit changes (not necessary if you're only reading data)
#     conn.commit()
