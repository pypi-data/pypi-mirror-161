from flask import request
from flask_restx import Resource, fields
import datetime
import pytz

def getServerInfoModel(appObj):
  serverInfoServerModel = appObj.flastRestPlusAPIObject.model('mainAPI', {
    'Version': fields.String(default='DEFAULT', description='Version of container running on server'),
    'APIAPP_APIDOCSURL': fields.String(default='',description='Base endpoint for EBO docs'),
    'APIAPP_FRONTENDURL': fields.String(default='',description='Base endpoint for frontend of app')
  })
  return appObj.flastRestPlusAPIObject.model('ServerInfo', {
    'Server': fields.Nested(serverInfoServerModel),
    'Derived': fields.Raw(required=False)
  })

def registerAPI(appObj, serverinfoapiprefix):

  ns = appObj.flastRestPlusAPIObject.namespace(serverinfoapiprefix, description='Public API for displaying server info.')

  @ns.route('/serverinfo')
  class servceInfo(Resource):

    '''General Server Operations'''
    @ns.doc('getserverinfo')
    @ns.marshal_with(getServerInfoModel(appObj))
    @ns.response(200, 'Success')
    def get(self):
     '''Get general information about the server'''
     curDatetime = datetime.datetime.now(pytz.utc)
     x = appObj.getDerivedServerInfoData()
     if x is None:
       return {
         'Server': {
           'Version': appObj.version ,
           'APIAPP_APIDOCSURL': appObj.globalParamObject.apidocsurl,
           'APIAPP_FRONTENDURL': appObj.globalParamObject.APIAPP_FRONTENDURL
         }
       }
     return {
      'Server': {
        'Version': appObj.version ,
        'APIAPP_APIDOCSURL': appObj.globalParamObject.apidocsurl,
        'APIAPP_FRONTENDURL': appObj.globalParamObject.APIAPP_FRONTENDURL
      },
      'Derived': x
     }
