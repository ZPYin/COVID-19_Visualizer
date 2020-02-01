import sqlite3 as db
from logger import logger


class virusDB():

    def __init__(self, dbFile):

        self.dbFile = dbFile

    def db_connect(self):
        """
        Connect/create the SQLite3 database.
        """

        conn = None
        try:
            conn = db.connect(self.dbFile)
            logger.info(db.version)
            logger.info(
                            'Successfully conect to the database:\n{}'.
                            format(self.dbFile)
                        )
        except db.Error as e:
            logger.warn(e)
            raise e

        self.conn = conn

    def db_create_overall_table(self):
        """
        create the database table.
        """

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS Overall (
                    id integer PRIMARY KEY,
                    time INT NOT NULL,
                    confirmedCount INT,
                    suspectedCount INT,
                    curedCount INT,
                    deadCount INT,
                    unique (time));
                """)
            self.conn.commit()

            logger.info('Create the Overall table successfully.')
        except db.Error as e:
            logger.error(e)
            return False

        return True

    def db_insert_overall_entry(self, entry):
        """
        insert data into the database.

        Parameters
        ----------
        entry: tuple

        History
        -------
        2019-10-01. First edition by Zhenping.
        """

        if type(entry) is dict:
            entry = [entry]

        for item in entry:

            item_tuple = (
                item['time'],
                item['confirmedCount'],
                item['suspectedCount'],
                item['curedCount'],
                item['deadCount']
            )
            try:
                c = self.conn.cursor()
                c.execute(
                    """
                    INSERT OR IGNORE INTO Overall(time, confirmedCount,
                    suspectedCount, curedCount, deadCount)
                    VALUES(?,?,?,?,?);
                    """,
                    item_tuple)
                self.conn.commit()
                c.close()

            except db.Error as e:
                logger.error(e)
                return False

        return True

    def db_drop_overall_table(self):
        """
        delete the overall table.
        """

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute(
                """DROP TABLE Overall;"""
            )
            self.conn.commit()

            logger.info('Delete the Overall successfully.')
        except db.Error as e:
            logger.error(e)
            return False

        return True

    def db_create_regionname_table(self):
        """
        create the database table.
        """

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute("""
                    CREATE TABLE IF NOT EXISTS Region_Name (
                        id integer PRIMARY KEY,
                        name TEXT,
                        unique(name));
                    """)
            self.conn.commit()

            logger.info('Create the Region_Name table successfully.')
        except db.Error as e:
            logger.error(e)
            return False

        return True

    def db_insert_regionname_entry(self, entry):
        """
        insert data into the database.

        Parameters
        ----------
        entry: tuple

        History
        -------
        2019-10-01. First edition by Zhenping.
        """

        if type(entry) is dict:
            entry = [entry]

        for item in entry:

            item_tuple = (
                item['name'],
            )
            try:
                c = self.conn.cursor()
                c.execute(
                    """INSERT OR IGNORE INTO Region_Name(name) VALUES (?);
                    """, item_tuple)
                self.conn.commit()
                c.close()

            except db.Error as e:
                logger.error(e)
                return

        return True

    def db_fetch_regionnames(self):

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute("""SELECT name, id from Region_Name;""")
            regionnames = c.fetchall()
            regionnames = dict(regionnames)
        except db.Error as e:
            logger.error(e)
            return None

        return regionnames

    def db_drop_regionname_table(self):
        """
        delete the Region_Name table.
        """

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute(
                """DROP TABLE Region_Name;"""
            )
            self.conn.commit()

            logger.info('Delete the Region_Name successfully.')
        except db.Error as e:
            logger.error(e)
            return False

        return True

    def db_create_regiondata_table(self):
        """
        create the database table.
        """

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute(
                """CREATE TABLE IF NOT EXISTS Region_Data (
                    id integer PRIMARY KEY,
                    provinceName TEXT,
                    provinceShortName TEXT,
                    confirmedCount INT,
                    suspectedCount INT,
                    curedCount INT,
                    deadCount INT,
                    comment TEXT,
                    country TEXT,
                    updateTime TEXT,
                    region_id INT,
                    CONSTRAINT fk_region_id
                    FOREIGN KEY (region_id)
                    REFERENCES Region_Name (id)
                );""")
            c.execute(
                """CREATE UNIQUE INDEX region_data_indx ON Region_Data
                (region_id, updateTime);""")
            self.conn.commit()

            logger.info(
                'Create the Region_Data table successfully.')
        except db.Error as e:
            logger.error(e)
            return False

        return True

    def db_insert_regiondata_entry(self, entry):
        """
        insert data into the database.

        Parameters
        ----------
        entry: tuple

        History
        -------
        2019-10-01. First edition by Zhenping.
        """

        if type(entry) is dict:
            entry = [entry]

        for item in entry:

            item_tuple = (
                item['provinceName'],
                item['provinceShortName'],
                item['confirmedCount'],
                item['suspectedCount'],
                item['curedCount'],
                item['deadCount'],
                item['country'],
                item['updateTime'],
                item['region_id']
            )
            try:
                c = self.conn.cursor()
                c.execute(
                    """INSERT OR IGNORE INTO Region_Data (provinceName, provinceShortName, confirmedCount, suspectedCount, curedCount, deadCount, country, updateTime, region_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", item_tuple)
                self.conn.commit()
                c.close()

            except db.Error as e:
                logger.error(e)
                return False

        return True

    def db_drop_regiondata_table(self):
        """
        delete the Region_Data table.
        """

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute(
                """DROP TABLE Region_Data;"""
            )
            self.conn.commit()

            logger.info('Delete the Region_Data successfully.')
        except db.Error as e:
            logger.error(e)
            return False

        return True

    def db_create_citydata_table(self):
        """
        create the database table.
        """

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute(
                """CREATE TABLE IF NOT EXISTS City_Data (
                id integer PRIMARY KEY,
                updateTime INT,
                cityName TEXT,
                confirmedCount INT,
                suspectedCount INT,
                curedCount INT,
                deadCount INT,
                region_id INT,
                country TEXT,
                CONSTRAINT fk_region_id
                FOREIGN KEY (region_id)
                REFERENCES Region_Name (id)
            );""")
            c.execute("""CREATE UNIQUE INDEX city_data_indx ON City_Data(region_id, cityName, updateTime)""")
            self.conn.commit()

            logger.info(
                'Create the City_Data table successfully.')
        except db.Error as e:
            logger.error(e)
            return False

        return True

    def db_insert_citydata_entry(self, entry):
        """
        insert data into the database.

        Parameters
        ----------
        entry: tuple

        History
        -------
        2019-10-01. First edition by Zhenping.
        """

        if type(entry) is dict:
            entry = [entry]

        for item in entry:

            item_tuple = (
                item['updateTime'],
                item['cityName'],
                item['confirmedCount'],
                item['suspectedCount'],
                item['curedCount'],
                item['deadCount'],
                item['country'],
                item['region_id']
            )
            try:
                c = self.conn.cursor()
                c.execute(
                    """INSERT OR IGNORE INTO City_Data (updateTime, cityName, confirmedCount, suspectedCount, curedCount, deadCount, country, region_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?);""", item_tuple)
                self.conn.commit()
                c.close()

            except db.Error as e:
                logger.error(e)
                return False

        return True

    def db_drop_citydata_table(self):
        """
        delete the Region_Data table.
        """

        if self.conn is None:
            logger.warn('database does not exist.')
            return False

        try:
            c = self.conn.cursor()
            c.execute(
                """DROP TABLE City_Data;"""
            )
            self.conn.commit()

            logger.info('Delete the City_Data successfully.')
        except db.Error as e:
            logger.error(e)
            return False

        return True

    def db_close(self):
        """
        close the database.
        """
        self.conn.close()
