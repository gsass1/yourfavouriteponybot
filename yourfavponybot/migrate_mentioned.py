"""This script migrates a mentioned.txt file to a sqlite3 database"""

from argparse import ArgumentParser
import sqlite3

def main():
    """
    The main method
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="The mentioned.txt file you want to migrate to SQL",
        metavar="FILE"
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        help="The output filename of the DB",
        metavar="FILE",
        default="mentioned.db"
    )
    args = parser.parse_args()

    conn = sqlite3.connect(args.output)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS mentioned (id INTEGER)")

    with open(args.input, "r") as input_file:
        values = []
        for line in input_file.read().splitlines():
            try:
                num = int(line)
            except ValueError:
                pass
            finally:
                values.append((num,))

        cursor.executemany("INSERT INTO mentioned VALUES (?)", values)
        conn.commit()

if __name__ == "__main__":
    main()
