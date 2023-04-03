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
            try:
                self.database_name = event._path
                getdb_(self.database_name)
                yield from [DatabaseOpenedEvent(event._path)]
            except:
                yield DatabaseOpenFailedEvent("Error while loading GUI")
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
            results = self.fetch_query_country(event)
            for row in results:
                yield CountrySearchResultEvent(Country(*row)) #One CountrySearchResultEvent for each country found in the search.
                                                                 # If no countries were found, no events are returned.
        elif isinstance(event,LoadCountryEvent):
            results = self.fetch_query_country(event)
            yield CountryLoadedEvent(Country(*results[0]))
        elif isinstance(event,SaveNewCountryEvent):
            try:
                self.insert_query_country(event)
                yield CountrySavedEvent(event.country())
            except sqlite3.IntegrityError as exe:
                yield SaveCountryFailedEvent("Failed to Add new Country due to duplicates")
                #If saving the country failed, SaveCountryFailedEvent
                                        # with a user-friendly error message.
        elif isinstance(event,SaveCountryEvent):
            try:
                result = self.update_query_country(event)
                yield CountrySavedEvent(event.country())
            except:
                yield SaveCountryFailedEvent("Updating the Database has failed")   #If saving the country failed,
                                        # SaveCountryFailedEvent with a user-friendly error message.


#################Region-related events################
        elif isinstance(event,StartRegionSearchEvent):
            results = self.fetch_query_region(event)
            for row in results:
                yield RegionSearchResultEvent(Region(*row))
        elif isinstance(event,LoadRegionEvent):
            results = self.fetch_query_region(event)
            yield RegionLoadedEvent(Region(*results[0]))

        elif isinstance(event,SaveNewRegionEvent):
            try:
                self.insert_query_region(event)
                yield RegionSavedEvent(event.region())
            except sqlite3.IntegrityError as exe:
                yield SaveRegionFailedEvent("Failed to Add new Region due to duplicates")
                #If saving the region failed, SaveRegionFailedEvent
                                        # with a user-friendly error message.
                    #If saving the country failed, SaveRegionFailedEvent
                                        # with a user-friendly error message.
        elif isinstance(event,SaveRegionEvent):
            try:
                result = self.update_query_region(event)
                yield RegionSavedEvent(event.region())
            except:
                yield SaveRegionFailedEvent("Updating the Database has failed")  #If saving the region failed,
                                        # SaveRegionFailedEvent with a user-friendly error message.
        else:ErrorEvent("Error in loading the app")
        yield from ()


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

#######################  helper functions for Country#################

    def fetch_query_country(self, event):
        # Define the query
        query = 'SELECT * FROM country c WHERE 1=1'
        query,param_tuple = self.query_formater_country(event, query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def insert_query_country(self, event):
        # Define the query
        query = "INSERT INTO country"

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed

        query,param_tuple = self.insert_query_formater_country(event.country(), query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def update_query_country(self, event):
        # Define the query
        query = 'UPDATE country SET'

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed
        query,param_tuple = self.update_query_formater_country(event.country(), query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def insert_query_formater_country(self, event, query):
        values = []
        columns = []
        params = []
        if "country_code" in event.__dir__() and not callable(event.country_code):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("country_code")
            params.append(event.country_code)
        if "name" in event.__dir__() and not callable(event.name):
            # query += " name = ?"
            values.append("?")
            columns.append("name")
            params.append(event.name)
        if "continent_id" in event.__dir__() and not callable(event.continent_id):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("continent_id")
            params.append(event.continent_id)
        if "wikipedia_link" in event.__dir__() and not callable(event.wikipedia_link):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("wikipedia_link")
            params.append(event.wikipedia_link)
        if "keywords" in event.__dir__() and not callable(event.keywords):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("keywords")
            params.append(event.keywords)

        columns_str = ", ".join(columns)
        values_str = ", ".join(values)

        # Append the column names and placeholders to the query string
        query += f"({columns_str}) VALUES ({values_str})"

        return query,params

    def update_query_formater_country(self, event, query):
        param_tuple = []
        if "country_code" in event.__dir__() and not callable(event.country_code):
            query += " country_code = ?,"
            param_tuple.append(event.country_code)
        if "name" in event.__dir__() and not callable(event.name):
            query += " name = ?,"
            param_tuple.append(event.name)
        if "continent_id" in event.__dir__() and not callable(event.continent_id):
            query += " continent_id = ?,"
            param_tuple.append(event.continent_id)
        if "wikipedia_link" in event.__dir__() and not callable(event.wikipedia_link):
            query += " wikipedia_link = ?,"
            param_tuple.append(event.wikipedia_link)
        if "keywords" in event.__dir__() and not callable(event.keywords):
            query += " keywords = ?,"
            param_tuple.append(event.keywords)
        query = query.rstrip(',')
        if "country_id" in event.__dir__() and not callable(event.country_id):
            query += " where country_id = ?"
            param_tuple.append(event.country_id)

        return query,param_tuple

    def query_formater_country(self, event, query):
        param_tuple = []
        if "country_code" in event.__dir__() and event.country_code():
            query += " AND country_code LIKE ?"
            country_code = '%' + event.country_code() + '%'
            param_tuple.append(country_code)
        if "name" in event.__dir__() and event.name():
            query += " AND name LIKE ?"
            name = '%' + event.name() + '%'
            param_tuple.append(name)
        if "country_id" in event.__dir__() and event.country_id():
            query += " AND country_id = ?"
            country_id = event.country_id()
            param_tuple.append(country_id)

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

#######################  helper functions for Region#################

    def fetch_query_region(self, event):
        # Define the query
        query = 'SELECT * FROM region r WHERE 1=1'
        query,param_tuple = self.query_formater_region(event, query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def insert_query_region(self, event):
        # Define the query
        query = "INSERT INTO region"

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed

        query,param_tuple = self.insert_query_formater_region(event.region(), query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def update_query_region(self, event):
        # Define the query
        query = 'UPDATE region SET'

        # name = event.name()
        # continent_code = event.continent_code()
        # Append optional conditions to the query string as needed
        query,param_tuple = self.update_query_formater_region(event.region(), query)
        results = getdb(self.database_name, query, param_tuple)
        return results

    def insert_query_formater_region(self, event, query):
        values = []
        columns = []
        params = []
        if "region_code" in event.__dir__() and not callable(event.region_code):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("region_code")
            params.append(event.region_code)
        if "local_code" in event.__dir__() and not callable(event.local_code):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("local_code")
            params.append(event.local_code)
        if "name" in event.__dir__() and not callable(event.name):
            # query += " name = ?"
            values.append("?")
            columns.append("name")
            params.append(event.name)
        if "continent_id" in event.__dir__() and not callable(event.continent_id):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("continent_id")
            params.append(event.continent_id)
        if "country_id" in event.__dir__() and not callable(event.country_id):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("country_id")
            params.append(event.country_id)

        if "wikipedia_link" in event.__dir__() and not callable(event.wikipedia_link):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("wikipedia_link")
            params.append(event.wikipedia_link)
        if "keywords" in event.__dir__() and not callable(event.keywords):
            # query += " continent_code = ?,"

            values.append("?")
            columns.append("keywords")
            params.append(event.keywords)

        columns_str = ", ".join(columns)
        values_str = ", ".join(values)

        # Append the column names and placeholders to the query string
        query += f"({columns_str}) VALUES ({values_str})"

        return query,params

    def update_query_formater_region(self, event, query):
        param_tuple = []
        if "region_code" in event.__dir__() and not callable(event.region_code):
            query += " region_code = ?,"
            param_tuple.append(event.region_code)
        if "local_code" in event.__dir__() and not callable(event.local_code):
            query += " local_code = ?,"
            param_tuple.append(event.local_code)
        if "name" in event.__dir__() and not callable(event.name):
            query += " name = ?,"
            param_tuple.append(event.name)
        if "continent_id" in event.__dir__() and not callable(event.continent_id):
            query += " continent_id = ?,"
            param_tuple.append(event.continent_id)
        if "country_id" in event.__dir__() and not callable(event.country_id):
            query += " country_id = ?,"
            param_tuple.append(event.country_id)
        if "wikipedia_link" in event.__dir__() and not callable(event.wikipedia_link):
            query += " wikipedia_link = ?,"
            param_tuple.append(event.wikipedia_link)
        if "keywords" in event.__dir__() and not callable(event.keywords):
            query += " keywords = ?,"
            param_tuple.append(event.keywords)
        query = query.rstrip(',')
        if "region_id" in event.__dir__() and not callable(event.region_id):
            query += " where region_id = ?"
            param_tuple.append(event.region_id)

        return query,param_tuple

    def query_formater_region(self, event, query):
        param_tuple = []
        if "region_code" in event.__dir__() and event.region_code():
            query += " AND region_code LIKE ?"
            region_code = '%' + event.region_code() + '%'
            param_tuple.append(region_code)
        if "local_name" in event.__dir__() and event.local_name():
            query += " AND local_name LIKE ?"
            local_name = '%' + event.local_name() + '%'
            param_tuple.append(local_name)
        if "name" in event.__dir__() and event.name():
            query += " AND name LIKE ?"
            name = '%' + event.name() + '%'
            param_tuple.append(name)
        if "region_id" in event.__dir__() and event.region_id():
            query += " AND region_id = ?"
            region_id = event.region_id()
            param_tuple.append(region_id)

            # Call the getdb function with the query
        return query,param_tuple
