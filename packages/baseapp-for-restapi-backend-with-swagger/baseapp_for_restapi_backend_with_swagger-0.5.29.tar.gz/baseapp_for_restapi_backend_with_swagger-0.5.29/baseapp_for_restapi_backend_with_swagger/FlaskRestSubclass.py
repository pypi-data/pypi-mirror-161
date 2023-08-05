from flask_restx import Api
from flask import url_for, render_template
import re
import json

#apidoc copied from restplus as it is not public
from .apidoc import Apidoc


# http://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus/
# https://flask-restplus.readthedocs.io/en/stable/
# https://github.com/noirbizarre/flask-restplus

#Moving apidocs blueprint so it is a member of this class not a global


import sys

def removeTrailingSlash(str):
  if str[-1:] != '/':
    return str
  return str[:-1]



# I need to subclass this in order to change the url_prefix for swaggerui
#  so I can reverse proxy everything under /apidocs
class FlaskRestSubclass(Api):
  internal_apidoc_prefix='/apidocs'
  internal_api_prefix='/api'
  internal_frontend_prefix='/frontend'

  complexReplaceString='dFDHf..kh543rrgefb..546t3rq54'

  bc_HTTPStatus_OK = None
  bc_HTTPStatus_NOT_FOUND = None
  bc_HTTPStatus_INTERNAL_SERVER_ERROR = None

  # Extra params inited manually
  apidocsurl = None
  APIDOCSPath = None
  overrideAPIDOCSPath = None
  APIPath = None
  localApiDoc = None

  def setExtraParams(self, apidocsurl, APIDOCSPath, overrideAPIDOCSPath, APIPath,internal_apidoc_prefix = '/apidocs',internal_api_prefix = '/api',internal_frontend_prefix = '/frontend'):
    self.apidocsurl = apidocsurl
    self.APIDOCSPath = APIDOCSPath
    self.overrideAPIDOCSPath = overrideAPIDOCSPath
    self.APIPath = APIPath
    self.internal_apidoc_prefix=internal_apidoc_prefix
    self.internal_api_prefix=internal_api_prefix
    self.internal_frontend_prefix=internal_frontend_prefix



  def __init__(self, *args, reverse=False, **kwargs):
      self._init_local_apidoc_variable(kwargs['doc'])
      super().__init__(*args, **kwargs)
      # Setup codes done this way because httpstatus isn't in python 3.3 or 3.4
      if sys.version_info[0] < 3.5:
        bc_HTTPStatus_OK = (200, 'OK', 'Request fulfilled, document follows')
        bc_HTTPStatus_NOT_FOUND = (404, 'Not Found','Nothing matches the given URI')
        bc_HTTPStatus_INTERNAL_SERVER_ERROR = (500, 'Internal Server Error','Server got itself in trouble')
      else:
        from http import HTTPStatus
        self.bc_HTTPStatus_OK = HTTPStatus.OK
        self.bc_HTTPStatus_NOT_FOUND = HTTPStatus.NOT_FOUND
        self.bc_HTTPStatus_INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR

  def get_swagger_static_internal_path(self, filename):
    #print('AAA')
    #print(self._doc) #/ebodocs/GenderV1/
    #print(filename) #swagger-ui.css
    #print(self.overrideAPIDOCSPath) #True or False
    #print(self.APIDOCSPath) #/apidocs

    #Only one global template is held so the last registered one is called
    # This means the wron EBO path will be selected
    # so I have had to use the replace method to correct it
    return self.complexReplaceString + '/swaggerui/bower/swagger-ui/dist/' + filename
    #return self.APIDOCSPath + '/swaggerui/bower/swagger-ui/dist/' + filename

  def _init_local_apidoc_variable(self, doc):
      self.localApiDoc = Apidoc('restplus_doc_' + doc, __name__,
          template_folder='templates',
          static_folder='static',
          static_url_path='/swaggerui',
      )
      # Registering internal function for use in templates
      self.localApiDoc.add_app_template_global(self.get_swagger_static_internal_path, name='swagger_static')

  #I don't want documentation to be registered here so overriding
  def _register_doc(self, app_or_blueprint):
      #if self._add_specs and self._doc:
      #    # Register documentation before root if enabled
      #    app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)
      ##app_or_blueprint.add_url_rule(self.prefix or '/', 'root', self.render_root)
      pass

  def _register_specs(self, app_or_blueprint):
    #Seems to be called twice. I don't know why
    pass

  def _register_apidoc(self, app):
    app_or_blueprint = self.blueprint or app
    conf = app.extensions.setdefault('restplus', {})
    configParamVal = 'apidoc_registered_' + self._doc
    if not conf.get(configParamVal, False):
      locToRegister = removeTrailingSlash(self._doc)
      self.localApiDoc.add_url_rule('/swagger.json', 'spec', self.getSwaggerJSON) #Register / will become /apidocs/swagger.json
      self.localApiDoc.add_url_rule('/', 'doc', self.render_doc)  #Register / will become /apidocs/

      app_or_blueprint.add_url_rule('/swagger.json', 'spec_api', self.getSwaggerJSON) #Register / will become /apis/swagger.json

      app.register_blueprint(self.localApiDoc, url_prefix=locToRegister)

    conf[configParamVal] = True

  # Flask will serve the files with the url pointing at /apidocs.
  #  if I have my reverse proxy serving it somewhere else I need to alter this
  def render_doc(self):
    '''Override this method to customize the documentation page'''
    if self._doc_view:
      return self._doc_view()
    elif not self._doc:
      self.abort(self.bc_HTTPStatus_NOT_FOUND)
    res = render_template('swagger-ui.html', title=self.title, specs_url=self.specs_url)
    res = res.replace(self.complexReplaceString,self.APIDOCSPath)

    regexp="\"https?:\/\/[a-zA-Z0\-9._]*(:[0-9]*)?" + self.internal_api_prefix.replace("/","\/") + "\/swagger.json\""
    regexp="\"https?:\/\/[a-zA-Z0\-9._]*(:[0-9]*)?" + self.internal_apidoc_prefix.replace("/","\/") + "\/swagger.json\""
    p = re.compile(regexp)
    res = p.sub("\"" + self.apidocsurl + "/swagger.json\"", res)
    '''
    if (self.overrideAPIDOCSPath()):
      #print("About to replace")
      #print(res)
      res = self.reaplcements(res)
      #print("Replaced")
      #print(res)
      #print("End")
    '''
    return res

  #By default swagger.json is registered as /api/swagger.json
  # as this is security protected I need this to be accessed in /apidocs/swagger.json as well
  def getSwaggerJSON(self):
    schema = self.__schema__
    return json.dumps(schema), self.bc_HTTPStatus_INTERNAL_SERVER_ERROR if 'error' in schema else self.bc_HTTPStatus_OK, {'Content-Type': 'application/json'}

  #Override the basepath given in the swagger file
  # I need to give out a different one from where the endpoint is registered
  @property
  def base_path(self):
    '''
    The API path
    :rtype: str
    '''
    return self.APIPath

  @property
  def specs_url(self):
      '''
      The Swagger specifications absolute url (ie. `swagger.json`)
      :rtype: str
      '''
      #return url_for('restplus_doc_' + self._doc + '.spec', _external=True)
      return self.apidocsurl + '/swagger.json'
