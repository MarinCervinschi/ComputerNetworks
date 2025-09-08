from typing import List, Dict
import csv


class CSV:
    @staticmethod
    def read(file_path: str) -> List[Dict[str, str]]:
        """
        Reads a CSV file and returns its contents as a list of dictionaries.
        Args:
            file_path (str): The path to the CSV file to be read.
        Returns:
            List[Dict[str, str]]: A list of dictionaries where each dictionary represents a row in the CSV file.
        Raises:
            Exception: If there is an error reading the file.
        """
        try:
            with open(file_path, encoding="utf-8") as file:
                reader = csv.DictReader(file)
                return [row for row in reader]
        except Exception as error:
            raise Exception(f"Error reading file: {error}")

    @staticmethod
    def get_by_key(file_path: str, key: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Retrieves rows from a CSV file that match the specified key-value pairs.

        Args:
            file_path (str): The path to the CSV file.
            key (Dict[str, str]): Dictionary of key-value pairs to match against each row.

        Returns:
            List[Dict[str, str]]: List of dictionaries representing rows that match all key-value pairs.

        Raises:
            Exception: If there is an error reading the file.
        """
        csv = CSV.read(file_path)
        if any(k not in csv[0] for k in key.keys()):
            raise Exception("Invalid key provided")
        
        return [elem for elem in csv if all(elem.get(k) == v for k, v in key.items())]
