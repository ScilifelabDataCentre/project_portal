import logging

from peewee import fn, JOIN
import tornado.web
import tornado

import db
import handlers
import portal_errors
import portal_utils


class AddDataset(handlers.StewardHandler):
    """
    Add a new Dataset to the db.
    """
    def post(self):
        """
        Add a dataset.

        Expects a JSON structure:
        ```
        {"dataset": {<dataset values>}}
        ```
        """
        data = tornado.escape.json_decode(self.request.body)
        if not 'dataset' in data:
            logging.info('AddDataset: bad request (dataset)')
            self.send_error(status_code=400)
            return

        ds_data = data['dataset']
        if 'title' not in ds_data or not ds_data['title']:
            logging.info('AddDataset: bad request (title)')
            self.send_error(status_code=400)
            return

        ds_to_add = {header: ds_data[header]
                     for header in ('title',
                                    'description',
                                    'doi',
                                    'creator',
                                    'contact',
                                    'dmp',
                                    'visible')
                     if header in ds_data}

        with db.database.atomic():
            ds_id = db.Dataset.create(**ds_to_add)

            for tag in ds_data['tags']:
                tag_id, _ = db.Tag.get_or_create(**tag)
                db.DatasetTag.create(dataset=ds_id,
                                     tag=tag_id)

            for publication in ds_data['publications']:
                pub_id, _ = db.Publication.get_or_create(**publication)
                db.DatasetPublication.create(dataset=ds_id,
                                             publication=pub_id)

            for data_url in ds_data['data_urls']:
                url_id, _ = db.DataUrl.get_or_create(**data_url)
                db.DatasetDataUrl.create(dataset=ds_id,
                                         data_url=url_id)

            for owner in ds_data['owners']:
                user_id, _ = db.User.get_or_create(**owner)
                db.DatasetOwner.create(dataset=ds_id,
                                       user=user_id)

        self.finish()


class CountryList(handlers.UnsafeHandler):
    """List countries."""
    def get(self):
        """
        Provide a JSON structure with country names:
        ```
        {"countries": [{"name": <country name>]}
        ```
        """
        self.write({'countries': [{'name': c} for c in self.country_list]})

    @property
    def country_list(self):
        return ["Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola",
                "Anguilla", "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba",
                "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh",
                "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia",
                "Bosnia and Herzegovina", "Botswana", "Brazil", "British Indian Ocean Territory",
                "British Virgin Islands", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
                "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands",
                "Central African Republic", "Chad", "Chile", "China", "Christmas Island",
                "Cocos Islands", "Colombia", "Comoros", "Cook Islands", "Costa Rica",
                "Croatia", "Cuba", "Curacao", "Cyprus", "Czech Republic",
                "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica",
                "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador",
                "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands",
                "Faroe Islands", "Fiji", "Finland", "France", "French Polynesia", "Gabon", "Gambia",
                "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada",
                "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
                "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq",
                "Ireland", "Isle of Man", "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan",
                "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait",
                "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
                "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Madagascar", "Malawi",
                "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania",
                "Mauritius", "Mayotte", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",
                "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru",
                "Nepal", "Netherlands", "Netherlands Antilles", "New Caledonia", "New Zealand",
                "Nicaragua", "Niger", "Nigeria", "Niue", "North Korea", "North Macedonia",
                "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestine",
                "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn",
                "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of the Congo", "Reunion",
                "Romania", "Russia", "Rwanda", "Saint Barthelemy", "Saint Helena",
                "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin", "Saint Pierre and Miquelon",
                "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
                "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
                "Sint Maarten", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
                "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan",
                "Suriname", "Svalbard and Jan Mayen", "Swaziland", "Sweden", "Switzerland", "Syria",
                "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tokelau", "Tonga",
                "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan",
                "Turks and Caicos Islands", "Tuvalu", "U.S. Virgin Islands", "Uganda", "Ukraine",
                "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
                "Vanuatu", "Vatican", "Venezuela", "Vietnam", "Wallis and Futuna", "Western Sahara",
                "Yemen", "Zambia", "Zimbabwe"]


class DeleteDataset(handlers.StewardHandler):
    """Delete a dataset"""
    def post(self):
        """
        Delete the dataset with the provided id.

        JSON structure:
        ```
        {"identifier": <ds_identifier> (int)}
        ```
        """
        data = tornado.escape.json_decode(self.request.body)
        try:
            identifier = int(data['identifier'])
        except ValueError:
            logging.info('DeleteDataset: bad request (input not an integer)')
            self.send_error(status_code=400, reason="The identifier should be an integer")
            return
        try:
            dataset = db.Dataset.get(db.Dataset.id == identifier)
        except db.Dataset.DoesNotExist:
            logging.info('AddDataset: bad request (dataset does not exist)')
            self.send_error(status_code=400, reason="Dataset does not exist")
            return
        dataset.delete_instance()

        self.finish()


class FindDataset(handlers.UnsafeHandler):
    """Find datasets matching a query"""
    def post(self):
        """
        Find datasets matching the query.

        Bad types will be ignored. No search will be performed if there are no valid terms.
        
        JSON structure:
        ```
        {"query": {"type": "value"}}
        ```
        """
        data = tornado.escape.json_decode(self.request.body)

        if portal_utils.has_rights(self.current_user, ('Steward', 'Admin')):
            query = (db.Dataset
                     .select(db.Dataset)
                     .join(db.DatasetOwner, JOIN.LEFT_OUTER)
                     .switch(db.Dataset)
                     .distinct()
                     .dicts())
        else:
            query = (db.Dataset
                     .select(db.Dataset)
                     .join(db.DatasetOwner, JOIN.LEFT_OUTER)
                     .switch(db.Dataset)
                     .where((db.Dataset.visible) |
                            (db.DatasetOwner.user == self.current_user))
                     .distinct()
                     .dicts())

        search_functions = {'title': lambda q, t: q.where(db.Dataset.title.contains(t)),
                            'creator': lambda q, c: q.where(db.Dataset.creator.contains(c)),
                            'tag': lambda q, t: (q.join(db.DatasetTag)
                                                 .join(db.Tag)
                                                 .switch(db.Dataset)
                                                 .where(db.Tag.title==t)),
                            'publication': lambda q, p: (q.join(db.DatasetPublication)
                                                         .join(db.Publication)
                                                         .switch(db.Dataset)
                                                         .where(db.Publication.identifier == p)),
                            'owner': lambda q, o: (q.switch(db.DatasetOwner)
                                                   .join(db.User)
                                                   .switch(db.Dataset)
                                                   .where(db.User.name == o))}

        used = False
        for search_type in data['query']:
            if search_type in search_functions:
                used = True
                query = search_functions[search_type](query, data['query'][search_type])

        if used:
            datasets = [dataset for dataset in query]
        else:
            self.send_error(status_code=400)
            return

        self.finish({'datasets': datasets})


class GetDataset(handlers.UnsafeHandler):
    """Retrieve a dataset."""
    def get(self, ds_identifier: str):
        """
        Retrieve the wanted dataset.

        Args:
            ds_identifier (str): the database id of the wanted dataset

        """
        dbid = int(ds_identifier)
        try:
            dataset = portal_utils.get_dataset(dbid, self.current_user)
        except db.Dataset.DoesNotExist:
            logging.info('GetDataset: dataset does not exist')
            self.send_error(status_code=404)
            return
        except portal_errors.InsufficientPermissions:
            logging.info('GetDataset: insufficient permissions')
            self.send_error(status_code=403)
            return

        self.finish(dataset)


class GetUser(handlers.UnsafeHandler):
    """Retrieve basic information about the current user."""
    def get(self):
        user = self.current_user

        ret = {'user': None, 'email': None}
        if user:
            ret = {'user': user.name,
                   'email': user.email,
                   'affiliation': user.affiliation,
                   'country': user.country}

        self.finish(ret)


class ListDatasets(handlers.UnsafeHandler):
    def get(self):
        user = self.current_user

        if portal_utils.has_rights(user, ('Steward', 'Admin')):
            ret = [dataset for dataset in (db.Dataset
                                           .select(db.Dataset.id, db.Dataset.title)
                                           .dicts())]
        else:
            ret = [dataset for dataset in (db.Dataset
                                           .select(fn.Distinct(db.Dataset.id), db.Dataset.title)
                                           .join(db.DatasetOwner, JOIN.LEFT_OUTER)
                                           .where((db.Dataset.visible) |
                                                  (db.DatasetOwner.user == user))
                                           .dicts())]

        self.finish({'datasets': ret})


class ListUsers(handlers.AdminHandler):
    """Retrieve a list of all users, including permissions etc."""
    def get(self):
        users = [user for user in db.User.select().dicts()]
        self.finish({'users': users})


class QuitHandler(handlers.UnsafeHandler):
    def get(self):  # pylint: disable=no-self-use
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.stop()
