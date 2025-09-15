# CXI-Template
Template fast-analysis code for CXI Experiments

### To set up the environment that is needed for this code, run the following commands.
```bash
conda init
conda config --append envs_dirs /sdf/group/lcls/ds/tools/conda_envs/
conda activate weber_group
ipython kernel install --user --name=weber_group --display-name "weber-group"
```

This will:
1. Set up your shell so that conda works properly.
2. Tell conda to look for environments in `/sdf/group/lcls/ds/tools/conda_envs/`
3. Activate the `weber_group` environment
4. Make the `weber_group` environment avaliable as a Jupyter kernel, called `weber-group`.

### You may need to restart your OnDemand session in order for these changes to take affect.
Once everything is done, check if it worked by hitting the "New Launcher" `+` icon in the upper right hand corner. Under the tabs for "Notebook" and "Console", you should see new entries for using the `weber-group` environment.
<p align="center">
  <img width="492" height="472" alt="Image" src="https://github.com/user-attachments/assets/38691a95-f2af-4b21-b65f-6aef25b8e28f" />
</p>
