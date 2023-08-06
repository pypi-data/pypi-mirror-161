JOB_DEFINITIONS = {
    "emtp": {
        "rid": "job-definition/cloudpss/emtp",
        "args": {
            "debug":
            "0",
            "n_cpu":
            "1",
            "solver":
            "0",
            "end_time":
            "1",
            "task_cmd":
            "",
            "step_time":
            "0.0001",
            "begin_time":
            "0",
            "task_queue":
            "",
            "initial_type":
            "0",
            "ramping_time":
            "0",
            "load_snapshot":
            "0",
            "save_snapshot":
            "0",
            "solver_option":
            "0",
            "output_channels": [{
                0: "aa",
                1: "1000",
                2: "compressed",
                3: "",
                4: [""]
            }],
            "max_initial_time":
            "1",
            "load_snapshot_name":
            "",
            "save_snapshot_name":
            "snapshot",
            "save_snapshot_time":
            "1"
        },
        "name": "电磁暂态仿真方案 1"
    },
    'sfemt': {
        "name": "移频电磁暂态仿真方案 1",
        "rid": "job-definition/cloudpss/sfemt",
        "args": {
            "begin_time":
            "0",
            "end_time":
            "1",
            "step_time":
            "0.0001",
            "output_channels": [{
                0: "aa",
                1: "1000",
                2: "compressed",
                3: "",
                4: [""]
            }],
            "solver":
            "0",
            "shift_freq":
            "50",
            "numerical_oscillation_suppression":
            "1",
            "ess":
            "0",
            "ess_time":
            "1e-6",
            "initial_type":
            "0",
            "ramping_time":
            "0",
            "max_initial_time":
            "1",
            "save_snapshot":
            "0",
            "save_snapshot_time":
            "1",
            "save_snapshot_name":
            "snapshot",
            "load_snapshot":
            "0",
            "load_snapshot_name":
            "",
            "task_queue":
            "",
            "solver_option":
            "0",
            "n_cpu":
            "1",
            "task_cmd":
            "",
            "debug":
            "0"
        }
    },
    "powerFlow": {
        "name": "潮流计算方案 1",
        "rid": "job-definition/cloudpss/power-flow",
        "args": {
            "UseBusVoltageAsInit": "1",
            "UseBusAngleAsInit": "1",
            "UseVoltageLimit": "1",
            "UseReactivePowerLimit": "1",
            "SkipPF": "0",
            "MaxIteration": "30"
        }
    }
}