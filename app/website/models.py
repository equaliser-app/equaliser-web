# -*- coding: utf-8 -*-


class User:

    def __init__(self, username, forename, surname, email, photo_url, phone,
                 token):
        self.username = username
        self.forename = forename
        self.surname = surname
        self.email = email
        self.photo_url = photo_url
        self.phone = phone
        self.token = token

    def to_dict(self):
        return {
            'username': self.username,
            'forename': self.forename,
            'surname': self.surname,
            'email': self.email,
            'photo_url': self.photo_url,
            'phone': self.phone,
            'token': self.token
        }

    @staticmethod
    def from_dict(dict_):
        return User(dict_['username'], dict_['forename'], dict_['surname'],
                    dict_['email'], dict_['photo_url'], dict_['phone'],
                    dict_['token'])

    @staticmethod
    def from_json(json):
        return User(json['username'], json['forename'], json['surname'],
                    json['email'], json['image']['sizes'][0]['url'],
                    json['phone'], json['token'])

    def __str__(self):
        return 'User(%s, %s)'.format(self.username, self.phone)


class Session:

    def __init__(self, user, token):
        self.user = user
        self.token = token

    def to_session(self, session):
        session['session'] = self.to_dict()

    def to_dict(self):
        return {
            'user': self.user.to_dict(),
            'token': self.token
        }

    @staticmethod
    def from_session(session):
        return Session.from_dict(session['session'])

    @staticmethod
    def from_dict(dict_):
        return Session(User.from_dict(dict_['user']), dict_['token'])

    @staticmethod
    def from_json(json):
        return Session(User.from_json(json['user']), json['token'])
