from utilities.test_runner import Runner


if __name__ == '__main__':
    from ultron.tests.factor.data.neutralize import Neutralize
    from ultron.tests.factor.data.quantile import Quantile
    from ultron.tests.factor.data.standardize import Standardize
    from ultron.tests.factor.data.winsorize import Winsorize
    from ultron.tests.optimize.linearbuild import LinearBuild
    from ultron.tests.optimize.longshortbuild import LongShortBuild
    from ultron.tests.optimize.meanvariancebuild import MeanVarianceBuild
    from ultron.tests.optimize.optimizers import Optimizers
    from ultron.tests.optimize.risk_model import RiskModel
    from ultron.tests.optimize.model.loader import Loader
    from ultron.tests.optimize.model.modelbase import ModelBase
    from ultron.tests.optimize.model.linearmodel import LinearModel
    from ultron.tests.optimize.model.treemodel import TreeModel

    runner = Runner([Neutralize,Quantile,Standardize,Winsorize,LinearBuild,
                    LongShortBuild,MeanVarianceBuild,Optimizers,RiskModel,
                    Loader,ModelBase,LinearModel,TreeModel])
    runner.run()