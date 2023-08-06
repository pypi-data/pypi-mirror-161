from wanda_api_parameters.parameters_api import open_model
import pywanda

def calc_time_step(pipe: pywanda.WandaComponent, nstep: int = 5):
    if pipe.is_pipe():
        tstep = pipe.get_property('Length').get_scalar_float() / (pipe.get_property('Wave speed').get_scalar_float() * nstep)
        return tstep


def calc_time_required(model: pywanda.WandaModel, nstep: int = 5):
    output = []
    tmin = 999
    # set calculation mode
    for pipe in model.get_all_pipes():
        pipe.get_property('Calculation mode').set_scalar(1)
    model.re_calculate_hcs()
    # Calculate minimum time step
    for pipe in model.get_all_pipes():
        try:
            output.append([
                pipe.get_name(),
                calc_time_step(pipe=pipe, nstep=nstep)
                        ])
            if output[-1][1] < tmin:
                tmin = output[-1][1]
        except:
            output.append([pipe.get_name(), 999])
    return output, tmin


def set_rigid(model: pywanda.WandaModel, tmin: float, nstep: int=5):
    for pipe in model.get_all_pipes():
        pipe.get_property('Calculation mode').set_scalar(1)
    model.re_calculate_hcs()
    # Calculate time step
    rigid_pipes = []
    for pipe in model.get_all_pipes():
        tstep = calc_time_step(pipe=pipe, nstep=nstep)
        if tstep <= tmin:
            print("Converting {} to rigid column (L={:.2f} m, C={:.2f} m/s)".format(
                pipe.get_name(),
                pipe.get_property('Length').get_scalar_float(),
                pipe.get_property('Wave speed').get_scalar_float()
            ))
            pipe.get_property('Calculation mode').set_scalar(2)
            rigid_pipes.append(pipe)
    return model, rigid_pipes



if __name__ == "__main__":
    fp = r"c:\Users\meerkerk\OneDrive - Stichting Deltares\Desktop\11207338 - Jubail - Model update"
    fn = "ASR_Future_Network.wdi"

    # Open model
    model = open_model(
        fn= fn,
        unzip= True,
        time_step = 1E-2,
        model_dir= fp,
        export_dir=fp,
    )
    output, tmin = calc_time_required(model=model)


    # Set rigid column
    model, rigid_pipes = set_rigid(model=model, tmin=1E-3)


