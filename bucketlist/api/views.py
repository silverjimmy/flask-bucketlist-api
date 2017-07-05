from flask import Blueprint, make_response, jsonify, request
from flask.views import MethodView

from bucketlist.models import Bucketlist, User

api_blueprint = Blueprint('api', __name__)


def check_duplicate_bucketlist(user_id, title):
    #  check if bucketlist exists
    if Bucketlist.query.filter_by(bucketlist_title=title, creator_id=user_id) \
                                 .first():
        return True


class Bucketlist_View(MethodView):
    def post(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            user_id = User.decode_auth_token(auth_token)
            post_data = request.get_json()
            title = post_data.get('title')

            if check_duplicate_bucketlist(user_id, title):
                response = {
                        'status': 'fail',
                        'message': 'Bucketlist already exists!'
                        }
                return make_response(jsonify(response)), 401

            try:
                new_bucketlist = Bucketlist(
                                 bucketlist_title=post_data.get('title'),
                                 creator_id=user_id
                                 )
                # insert the bucketlist
                new_bucketlist.save()
                response = {
                            'status': 'success',
                            'message': 'Bucketlist {} has been added'
                            .format(post_data.get('title'))
                            }
                return make_response(jsonify(response)), 201
            except Exception as e:
                response = {
                            'status': 'fail' + str(e),
                            'message': 'Some error occurred. Please try again'
                            }
                return make_response(jsonify(response)), 401

        else:
            response = {
                        'status': 'fail',
                        'message': 'Please provide a valid auth token!'
                        }
            return make_response(jsonify(response)), 401


add_bucket_view = Bucketlist_View.as_view('addbucket_api')

# add rules for API endpoints
api_blueprint.add_url_rule(
    '/api/v1/bucketlist/',
    view_func=add_bucket_view,
    methods=['POST']
)
