
# Note: TYPE is a reserved keyword in the parameters for each source
# This static generator will create any type of connector -- need to add new types to this method
def _GetExecutor(parameters, streams=None, schedule=None, datastream=None):
    if 'TYPE' in parameters:
        type_lower = parameters['TYPE'].lower()
    elif 'type' in parameters:
        type_lower = parameters['type'].lower()
    else:
        print("ERROR: Cannot create Connector with parameters {} since TYPE is not defined".format(parameters))
        return None
    
    if type_lower=='prefect':
        #print("Created Prefect executor...")
        return Prefect_Executor(parameters, streams=streams, schedule=schedule, datastream=datastream)
    

##############################
### Parent Executor class ###
class Executor:
    parameters = None
    connection = None
    
    def __init__(self, parameters, required=None):
        self.parameters = parameters
        
        # If provided a list of required parameters, then confirm that each one is defined
        if required is not None:
            for param in required:
                if param not in parameters:
                    print("ERROR: Required parameter {} has not been defined for this connector of type {}".format(param, 
                                                                                                                   type(self)))
                    raise
        
    def connect(self):
        return
    
    def execute(self):
        return
    
    def deploy(self):
        return
    
    
#######################################
### Prefect executor ###
from prefect import Task, Flow, task, Parameter

# WARNING: THE LOCATION OF THIS DATASTREAM DIRECTORY IS HARD-CODED HERE. SHOULD BE GENERALIZED BETTER THAN THIS.

@task
def prefect_deploy_task(datastream_def, dataflow_label, **kwargs):
    print("Loading DataStream with definition: {}".format(datastream_def))
    import sys
    sys.path.append("/data/lib/")
    from DataStream import DataStream
    ds = DataStream(directory=datastream_def['directory'],
                    config=datastream_def['config'],
                    register=False  # Must be false or we have an infinite loop
                   )
    print("Deploying '{}'".format(dataflow_label))
    ds.deploy(dataflow_label, **kwargs)

@task
def prefect_run_task(#datastream_def, 
                     datastream_dir, datastream_config, dataflow_label, **kwargs):
    print("Loading DataStream with dir: {}, config file: {}".format(datastream_dir, datastream_config))
    import sys
    sys.path.append("/data/lib/")
    from DataStream import DataStream
    # Allow directory/config to be overriden as parameters sent in by Prefect
    ds = DataStream(directory=datastream_dir, #datastream_def['directory'],
                    config=datastream_config, #datastream_def['config'],
                    register=False  # Must be false or we have an infinite loop
                   )
    print("Running '{}'".format(dataflow_label))
    ds.run(dataflow_label, **kwargs)

class Prefect_Executor(Executor):
    required_params = []
    prefect_tasks = {}
    prefect_flows = {}
    
    def __init__(self, parameters, streams=None, schedule=None, datastream=None):
        Executor.__init__(self, parameters, required=self.required_params)
        
        # Built-in support for Prefect tasks/flows 
        self.prefect_tasks = {}
        self.prefect_flows = {}
        #print("Received datastream def:", datastream)
        self.datastream_def = datastream
        
        # By default create these Tasks
        self.prefect_project = parameters.get('project', None)
        self.prefect_tasks['deploy'] = prefect_deploy_task
        self.prefect_tasks['run'] = prefect_run_task

        # Create default flows
        #self._create_flow('deploy')
        #self._create_flow('run')

        # Create Prefect Flows for each "stream" we defined in the config file
        if streams is not None:
            #print("Creating streams: {}".format(streams))
            for stream_label in streams:
                stream_flows = streams[stream_label]
                #print("Creating Prefect Flow '{}' for running these in sequence:".format(stream_label), stream_flows)
                stream_schedule = None
                if schedule is not None:
                    #schedules_def = datastream['schedule']
                    stream_schedule = schedule.get(stream_label, None)
                    #print("...using this schedule:", stream_schedule)
                self._create_flow_stream('run', stream_label, stream_flows, stream_schedule=stream_schedule)

                # Only register these new flows to the Prefect Cloud project if flagged
                #if self.register_flows and self.prefect_project is not None:
                #    self.prefect_flows[stream].register(project_name=self.prefect_project)

    # Set up flows too
    def _create_flow(self, flow_type, flow_name=None):
        this_flow = Flow(flow_name or flow_type)
        dataflow_label_param = Parameter('dataflow_label', default='')
        this_prefect_task = self.prefect_tasks[flow_type].copy()
        this_prefect_task.skip_on_upstream_skip = False
        this_flow.add_task(this_prefect_task)
        this_prefect_task.bind(#datastream_def=self.datastream_def,
                               datastream_dir=self.datastream_def['directory'],
                               datastream_config=self.datastream_def['config'],
                               dataflow_label=dataflow_label_param, 
                               flow=this_flow)
        self.prefect_flows[flow_type] = this_flow

    def runPrefectTask(self, task_type, flow, **kwargs):
        if task_type in self.prefect_tasks:
            prefect_task_obj = self.prefect_tasks[task_type].copy()
            prefect_task_obj.run(flow, **kwargs)
        else:
            print("Cannot find Prefect task with label '{}'".format(task_type))
    
    # TODO: Allow other kwargs to pass-through to deploy/run
    def runPrefectFlow(self, task_type, flow=None):
        if task_type in self.prefect_flows:
            prefect_flow_obj = self.prefect_flows[task_type]
            if flow is not None:
                prefect_flow_obj.run(parameters={'dataflow_label': flow})
            else:
                prefect_flow_obj.run()
        else:
            print("Cannot find Prefect Flow with type '{}'".format(task_type))

    # Converts the given schedule (using our own dict structure) into a well-formatted cronjob schedule string
    def get_cron_clock_strings(self, schedule):
        # Example: {"frequency": "daily", "when": [[11,20], [23,20]]} --> '20 11 * * *', '20 23 * * *'
        clock_strings = []
        frequency = schedule['frequency']
        when = schedule['when']
        if frequency=='daily':
            # Assume 'when' is a list of times (each of which is an [hour,min] pair)
            for run_time in when:
                run_hour, run_min = run_time
                cron_string = "{} {} * * *".format(run_min, run_hour)
                clock_strings.append(cron_string)
        elif frequency=='weekly':
            # Assume 'when' here is a list of days of the week + times, like [[Tuesday, [11,0]]]
            dayofweek_nums = {0:['sunday', 'sun', 's'],
                              1:['monday', 'mon', 'm'],
                              2:['tuesday', 'tues', 't'],
                              3:['wednesday', 'wed', 'w'],
                              4:['thursday', 'thur', 'thurs', 'th'],
                              5:['friday', 'fri', 'f'],
                              6:['saturday', 'sat', 'sa']}

            for weekly_daytime in when:
                run_dayofweek, run_time = weekly_daytime
                run_hour, run_min = run_time
                run_dayofweek_num = [num for num, daystrings in dayofweek_nums.items() if run_dayofweek.lower() in daystrings][0]
                #print("Using dayofweek #={} for '{}'".format(run_dayofweek_num, run_dayofweek))
                cron_string = "{} {} * * {}".format(run_min, run_hour, run_dayofweek_num)
                clock_strings.append(cron_string)
        return clock_strings


    def _create_flow_stream(self, flow_type, stream, flow_list, stream_schedule=None):
        this_flow = Flow(stream)
        previous_task = None
        this_prefect_schedule = None

        # Set up the tasks to run in this flow
        this_datastream_dir_param = Parameter('datastream_dir', default=self.datastream_def.get('directory', '/'))
        this_datastream_config_param = Parameter('datastream_config', default=self.datastream_def.get('config', '/'))
        for i, flow in enumerate(flow_list):
            this_param = Parameter('flow_{}'.format(i), default=flow)
            this_prefect_task = self.prefect_tasks[flow_type].copy() if previous_task is None else this_prefect_task.copy()
            this_flow.add_task(this_prefect_task)
            this_prefect_task.bind(#datastream_def=self.datastream_def,
                                   datastream_dir=this_datastream_dir_param,
                                   datastream_config=this_datastream_config_param,
                                   dataflow_label=this_param, 
                                   flow=this_flow)
            this_prefect_task.name = flow

            # Add dependencies on the previous task
            if previous_task is not None:
                this_flow.set_dependencies(task=this_prefect_task, upstream_tasks=[previous_task])
            previous_task = this_prefect_task

        # If provided, set this flow to run on a schedule
        if stream_schedule is not None:
            #print("...set schedule:", stream_schedule)
            cron_clock_strings = self.get_cron_clock_strings(stream_schedule)
            #print("...cron strings:", cron_clock_strings)
            import pendulum
            from prefect.schedules import Schedule
            from prefect.schedules.clocks import CronClock

            # Make sure we have 1+ cron strings to schedule
            if len(cron_clock_strings)>0:
                this_clock_pendulum = pendulum.datetime(2019, 1, 1, tz="America/Los_Angeles")
                this_prefect_schedule = schedule = Schedule(clocks=[CronClock(cron_clock_string, start_date=this_clock_pendulum) for cron_clock_string in cron_clock_strings])
                this_flow.schedule = this_prefect_schedule

        self.prefect_flows[stream] = this_flow


    def connect(self, type='connection'):
        super().connect()
        
        if self.parameters is not None:
            print("Connecting to Prefect:", self.parameters)
        
    def execute(self):
        super().execute()
        
    def deploy(self, flows='*'):
        super().deploy()
        
        flows_to_deploy = self.prefect_flows if flows=='*' else [flows] if isinstance(flows, str) else flows
        
        # Register these new flows to the Prefect Cloud project
        if self.prefect_project is not None:
            for flow in flows_to_deploy:
                if flow in self.prefect_flows:
                    flow_obj = self.prefect_flows[flow]
                    flow_obj.register(project_name=self.prefect_project)
                else:
                    print("WARNING: Cannot deploy flow '{}' since it's not stored for this Executor".format(flow))
                    
#         if self.register_flows and self.prefect_project is not None:
#             self.prefect_flows['deploy'].register(project_name=self.prefect_project)
#             self.prefect_flows['run'].register(project_name=self.prefect_project)
    
    