"""Functions for optimising the WT."""
import logging
log = logging.getLogger(__name__)


def wtopt_r2(rxn, model_clean, eps):
    with model_clean:  # Keeps the modifications to within the with
        # change the objective to the reaction:
        model_clean.objective = rxn
        # optimize for that objective
        FBA = model_clean.optimize(objective_sense="maximize")
        FBA_sol = FBA.objective_value
        log.info("FBA sol: " + str(FBA_sol))
        # set the new bounds as a percentage of the solution
        if FBA_sol > 0:
            lower_bound = FBA_sol * eps
            upper_bound = rxn.upper_bound
        else:
            with model_clean:
                model_clean.objective = rxn
                FBA = model_clean.optimize(objective_sense="minimize")
                FBA_sol = FBA.objective_value
            # print("Min: " + str(FBA_sol))
            lower_bound = FBA_sol * eps
            upper_bound = 1000  # redundant? questionable? what about backwards reactions?
    return lower_bound, upper_bound


def optimise_wt(model, biomass):
    log.info("Objective: "+str(model.objective))
    fbag = model.optimize()  # The optimized objective value
    # The minimum objective value we want to reach:
    obj = biomass * fbag.objective_value
    log.info("Final obj value: "+str(biomass)+"*"+str(fbag.objective_value)+"="+str(obj))
    return obj
