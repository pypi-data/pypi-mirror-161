
def getPaginatedParamValues(request):
  pagesizemax = 500
  offset = request.args.get('offset')
  if offset is None:
    offset = 0
  else:
    offset = int(offset)
  pagesize = request.args.get('pagesize')
  if pagesize is None:
    pagesize = 100
  else:
    pagesize = int(pagesize)
  if pagesize > pagesizemax:
    pagesize = pagesizemax
  
  sort = request.args.get('sort')
  query = request.args.get('query')
  return {
    'offset': offset,
    'pagesize': pagesize,
    'query': query,
    'sort': sort,
  }

