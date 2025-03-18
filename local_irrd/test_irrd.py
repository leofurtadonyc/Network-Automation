#!/usr/bin/env python3
"""
A simple Python tool to play around with your local IRRd API.
This script submits an RPSL object change to your IRRd instance.
"""

import requests
import json

def submit_rpsl_change(api_url, rpsl_text, passwords):
    """
    Submits an RPSL object change to the IRRd API.
    
    Args:
        api_url (str): The API endpoint URL.
        rpsl_text (str): The complete RPSL object as a string.
        passwords (list): List of passwords for authentication.
        
    Returns:
        dict: JSON response from the API.
    """
    payload = {
        "objects": [{"object_text": rpsl_text}],
        "passwords": passwords
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "response": response.text if response else "No response"}

def main():
    # URL for your local IRRd instance API endpoint.
    # Adjust the port if your HTTP API is running on a different one.
    # api_url = "http://127.0.0.1:8080/submit/"
    api_url = "http://127.0.0.1:8080/v1/submit/"
    
    # Example RPSL object text (customize this as needed)
    rpsl_text = (
        "route:         192.0.2.0/24\n"
        "origin:        AS12345\n"
        "mnt-by:        MAINT-TEST\n"
        "source:        IRRD"
    )

    # rpsl_text = (
    #     "route:         192.0.2.0/24\n"
    #     "origin:        AS12345\n"
    #     "mnt-by:        EXAMPLE-MNT\n"
    #     "source:        ALTDB"
    # )

    # Your authentication password(s)
    passwords = ["Juniper"]
    
    print("Submitting RPSL object change to:", api_url)
    result = submit_rpsl_change(api_url, rpsl_text, passwords)
    print("Response from IRRd API:")
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
