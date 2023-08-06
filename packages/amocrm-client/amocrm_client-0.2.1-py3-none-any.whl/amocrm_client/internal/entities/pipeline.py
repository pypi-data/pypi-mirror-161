from .entity import Entity


class Pipeline(Entity):

	async def get(self, with_pipe_id=False):
		amo = super().amo_init()
		pipelines = await amo.pipeline.get()
		if not pipelines['result']:
			return pipelines
		for pipe in pipelines['data']:
			pipe['statuses'] = {status['name']: status for status in pipe['_embedded']['statuses']}
			pipe.pop('_embedded')
		if with_pipe_id:
			data = {pipe['id']: pipe for pipe in pipelines['data']}
		else:
			data = {pipe['name']: pipe for pipe in pipelines['data']}
		return {'result': True, 'data': data}
