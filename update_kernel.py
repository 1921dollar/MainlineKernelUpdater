#!/usr/bin/python3
"""

This script easily updates your Linux kernel to the latest mainline kernel.
Right now it only works on Ubuntu amd64 but more platforms are planned.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = "Joseph Lenzi"
__copyright__ = "Copyright 2019 Joseph Lenzi."
__date__ = "04/20/2019"
__license__ = "GPLv3"
__maintainer__ = "1921dollar"
__status__ = "Production"
__version__ = "0.0.1"

"""

import time
import wget
import requests
import subprocess

def main():
    os_result = subprocess.run(['awk -F= \'/^NAME/{print $2}\' /etc/os-release'], stdout=subprocess.PIPE, shell=True)
    os_result = os_result.stdout.decode('utf-8')
    if ("Ubuntu" in os_result):
        mainline_kernel_page = requests.get('https://kernel.ubuntu.com/~kernel-ppa/mainline/').content.decode('utf-8')
        table_start_pos = mainline_kernel_page.index("<table>") + len("<table>")
        table_end_pos = mainline_kernel_page.index("</table>", table_start_pos)
        table_contents = mainline_kernel_page[table_start_pos:table_end_pos]
        table_contents = table_contents.split("<tr>")
        links = []
        version_names = []
        versions = []
        for row in table_contents:
            if "<td " in row and "<a href=\"v" in row:
                link_start_pos = row.index("<a href=\"") + len("<a href=\"")
                link_end_pos = row.index("\">", link_start_pos)
                link = row[link_start_pos:link_end_pos]
                if "-" not in link:
                    links.append(link)
                    
                    version_start_pos = 1
                    version_end_pos = len(link)-1
                    version_name = link[version_start_pos:version_end_pos]
                    version_names.append(version_name)
                    
                    # Shorten version_name to only 5 chars
                    version_name = version_name[0:5]
                    version = float(version_name.replace(".", ""))
                    versions.append(version)
    
        latest_version = max(versions, key=float)
        latest_version_ind = versions.index(latest_version)
        print("Latest version available: " + version_names[latest_version_ind])
        
        # Is version installed?
        kernel_result = subprocess.run(['apt list --installed | grep linux-headers-' + version_names[latest_version_ind]], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
        kernel_result = kernel_result.stdout.decode('utf-8')
        kernel_result = kernel_result.split('\n')
        
        # Do we need to upgrade?
        if (len(kernel_result) == 1):
            print("Downloading and installing latest mainline kernel...")
            time.sleep(5)
            download_listing_page_link = links[latest_version_ind]
            download_listing_page = requests.get('https://kernel.ubuntu.com/~kernel-ppa/mainline/' + download_listing_page_link).content.decode('utf-8')
    
            # Only support amd64
            uname_result = subprocess.run(['uname -mrs'], stdout=subprocess.PIPE, shell=True)
            uname_result = uname_result.stdout.decode('utf-8')
            if ("x86_64" in uname_result):
                # Get link listing
                link_listing_start = download_listing_page.index("BUILD.LOG.amd64</a>):<br>") + len("BUILD.LOG.amd64</a>):<br>")
                link_listing_end = download_listing_page.index("<br>\n<br>", link_listing_start)
                link_listings = download_listing_page[link_listing_start:link_listing_end]
                link_listings = link_listings.split("<a")
                
                linux_headers_all_link = ""
                linux_headers_generic_link = ""
                linux_modules_generic_link = ""
                linux_image_generic_link = ""
                
                for link_listing in link_listings:
                    # Get linux headers all .deb link
                    if "linux-headers" in link_listing and "_all.deb" in link_listing:
                        linux_headers_all_start = link_listing.index("href=\"") + len("href=\"")
                        linux_headers_all_end = link_listing.index("\"", linux_headers_all_start)
                        linux_headers_all_link = link_listing[linux_headers_all_start:linux_headers_all_end]
                
                    # Get linux headers generic .deb link
                    if "linux-headers" in link_listing and "-generic" in link_listing:
                        linux_headers_generic_start = link_listing.index("href=\"") + len("href=\"")
                        linux_headers_generic_end = link_listing.index("\"", linux_headers_generic_start)
                        linux_headers_generic_link = link_listing[linux_headers_generic_start:linux_headers_generic_end]
    
                    # Get linux modules generic .deb link
                    if "linux-modules" in link_listing and "-generic" in link_listing:
                        linux_modules_generic_start = link_listing.index("href=\"") + len("href=\"")
                        linux_modules_generic_end = link_listing.index("\"", linux_modules_generic_start)
                        linux_modules_generic_link = link_listing[linux_modules_generic_start:linux_modules_generic_end]
                    
                    # Get linux image unsigned generic .deb link
                    if "linux-image-unsigned" in link_listing and "-generic" in link_listing:
                        linux_image_generic_start = link_listing.index("href=\"") + len("href=\"")
                        linux_image_generic_end = link_listing.index("\"", linux_image_generic_start)
                        linux_image_generic_link = link_listing[linux_image_generic_start:linux_image_generic_end]
                
                if (linux_headers_all_link != "" and linux_headers_generic_link != "" and linux_modules_generic_link != "" and linux_image_generic_link != ""):
                    # Download and install linux headers all .deb link
                    print("Downloading " + linux_headers_all_link + "...")
                    wget.download('https://kernel.ubuntu.com/~kernel-ppa/mainline/' + download_listing_page_link + linux_headers_all_link, "/tmp/" + linux_headers_all_link)
                    print("\nInstalling " + linux_headers_all_link + "...")
                    subprocess.run(['dpkg -i /tmp/' + linux_headers_all_link], stdout=subprocess.PIPE, shell=True)
                    
                    # Download and install linux headers generic .deb link
                    print("Downloading " + linux_headers_generic_link + "...")
                    wget.download('https://kernel.ubuntu.com/~kernel-ppa/mainline/' + download_listing_page_link + linux_headers_generic_link, "/tmp/" + linux_headers_generic_link)
                    print("\nInstalling " + linux_headers_generic_link + "...")
                    subprocess.run(['dpkg -i /tmp/' + linux_headers_generic_link], stdout=subprocess.PIPE, shell=True)
                    
                    # Download and install linux modules generic .deb link
                    print("Downloading " + linux_modules_generic_link + "...")
                    wget.download('https://kernel.ubuntu.com/~kernel-ppa/mainline/' + download_listing_page_link + linux_modules_generic_link, "/tmp/" + linux_modules_generic_link)
                    print("\nInstalling " + linux_modules_generic_link + "...")
                    subprocess.run(['dpkg -i /tmp/' + linux_modules_generic_link], stdout=subprocess.PIPE, shell=True)
                    
                    # Download and install linux image unsigned generic .deb link
                    print("Downloading " + linux_image_generic_link + "...")
                    wget.download('https://kernel.ubuntu.com/~kernel-ppa/mainline/' + download_listing_page_link + linux_image_generic_link, "/tmp/" + linux_image_generic_link)
                    print("\nInstalling " + linux_image_generic_link + "...")
                    subprocess.run(['dpkg -i /tmp/' + linux_image_generic_link], stdout=subprocess.PIPE, shell=True)
        else:
            print("You already have the latest kernel installed.")

main()