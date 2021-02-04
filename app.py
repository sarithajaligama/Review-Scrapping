import os
from urllib.request import urlopen as uReq

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from flask import Flask, render_template, request
from flask_cors import cross_origin

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    global custComment
    if request.method == 'POST':
        #try:
            # ==============================================================================
            def get_HTML_from_URL(URL):
                req = requests.get(URL)  # Get the Page request from URL
                html_content = req.content  # Extract the HTML content from the URL
                html_content_bs = bs(html_content, "html.parser")  # Beautify HTML Content
                req.close()  # Closing the requested page
                return html_content_bs  # returning the beautified HTML content

            # ==============================================================================
            webLink = "https://www.flipkart.com"
            #searchString = "honor"  # "fastrack watch"
            searchString = request.form['content'].replace(' ', '')

            # ==============================================================================
            URL = webLink + "/search?q=" + searchString
            searchString_HTML = get_HTML_from_URL(URL)

            # ==============================================================================
            firstProd_link = searchString_HTML.find('div', {'class': '_13oc-S'}).a['href']
            URL = webLink + firstProd_link
            firstProd_HTML = get_HTML_from_URL(URL)

            # ==============================================================================
            reviews_html = firstProd_HTML.findAll('div', {"class": "col JOpGWq"})
            reviews_html = reviews_html[0]

            # ==============================================================================
            all_reviews_link = webLink + list(reviews_html)[5]['href']  # Get all reviews link
            all_Reviews_html = get_HTML_from_URL(all_reviews_link)  # Get HTML code of all reviews

            # ==============================================================================
            # Number of pages of all comments
            footer_content = all_Reviews_html.findAll('div', {'class': "_1AtVbE col-12-12"})[-1]
            n_pages = int(footer_content.div.div.span.text.split()[-1])

            # Page common link===============================================================
            pages_common_link = footer_content.div.div.nav.a['href'][:-1]
            page_link = webLink + pages_common_link + str(1)  # Get Page Link

            # ==============================================================================
            commentboxes = get_HTML_from_URL(page_link)  # Get HTML code of a page
            n_records = commentboxes.findAll('div', {'class': "_1AtVbE col-12-12"})[
                        4:-1]  # Get HTML of all comments in each page

            reviews = pd.DataFrame(columns=["Product_Name", "Customer_Name", "Rating", "Heading",
                                            "Comment", "Date", "Location"])

            # reviews = []
            def extract_comments(commentbox):

                # Customer_Name -----------------------
                try:
                    Customer_Name = commentbox.findAll('p', {'class': "_2sc7ZR _2V5EHH"})[0].text
                except:
                    Customer_Name = 'None'

                # Customer_Rating ---------------------
                try:
                    Rating = int(commentbox.find('div', {'class': '_3LWZlK _1BLPMq'}).text[0])
                except:
                    Rating = 0

                # Comment_Heading ---------------------
                try:
                    Heading = commentbox.find('p', {'class': '_2-N8zT'}).text
                except:
                    Heading = "None"

                # Comment_Text ---------------------
                try:
                    Comment = commentbox.find_all('div', {'class': 't-ZTKy'})[0].text
                except:
                    Comment = 'None'

                # Comment_Date ---------------------
                try:
                    Date = list(commentbox.find('div', {'class': 'row _3n8db9'}).div)[-1].text
                except:
                    Date = 'None'

                # Comment_from_location ---------------------
                try:
                    Location = list(list(commentbox.find('div', {'class': 'row _3n8db9'}).div)[2])[-1].text[2:]
                except:
                    Location = 'None'

                # Creating Dictionary
                comment_record = {"Product_Name" : searchString, 'Customer_Name': Customer_Name, 'Rating': Rating,
                                  'Heading': Heading, 'Comment': Comment, 'Date': Date,
                                  'Location': Location}

                return comment_record

            for j in range(len(n_records)):
                record = n_records[j]
                # Calling function to create a comment record
                comment_record = extract_comments(record)

                # Appending into dataframe
                reviews = reviews.append(comment_record, ignore_index=True)


            return render_template('results.html', reviews=reviews)


        #except Exception as e:
            #print('The Exception message is: ', e)
            #return 'something is wrong'
            # return render_template('results.html')

    else:
        return render_template('index.html')

#port = int(os.getenv("PORT",5011))
if __name__ == "__main__":
    app.run(debug=True, port=5011)
    #app.run(host='0.0.0.0', port=port)
    # app.run(host='127.0.0.1', port=8001, debug=True)
