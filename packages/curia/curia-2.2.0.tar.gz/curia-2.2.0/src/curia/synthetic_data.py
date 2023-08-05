import logging
import math

import numpy as np
import pandas as pd
from numpy.random import binomial, multivariate_normal, normal, uniform
from sklearn.model_selection import train_test_split


# pylint: disable=bad-option-value,bad-continuation,too-many-locals,too-many-statements,logging-format-interpolation,logging-fstring-interpolation,consider-using-f-string


def generate_data(
        binary_treatment: bool = True,
        binary_outcome: bool = False,

        n_train: int = 1000,
        n_test: int = 100,

        binary_dim: int = 5,
        uniform_dim: int = 5,
        normal_dim: int = 5,

        n_confounders: int = 2,
        n_features_outcome: int = 3,
        n_features_treatment_effect: int = 3,
        n_features_propensity: int = 3,

        outcome_noise_sd: int = 1,

        missing_data_scaler: float = 0.5,

        treatment_share_scaler: float = 0.05,

        # Random seed
        seed: int = 42) -> object:
    """

    Parameters
    ----------
    binary_treatment: bool :
         (Default value = True)
    binary_outcome: bool :
         (Default value = False)
    n_train: int :
         (Default value = 1000)
    n_test: int :
         (Default value = 100)
    binary_dim: int :
         (Default value = 5)
    uniform_dim: int :
         (Default value = 5)
    normal_dim: int :
         (Default value = 5)
    n_confounders: int :
         (Default value = 2)
    n_features_outcome: int :
         (Default value = 3)
    n_features_treatment_effect: int :
         (Default value = 3)
    n_features_propensity: int :
         (Default value = 3)
    outcome_noise_sd: int :
         (Default value = 1)
    missing_data_scaler: float :
         (Default value = 0.5)
    treatment_share_scaler: float :
         (Default value = 0.05)
    # Random seedseed: int :
         (Default value = 42)

    Returns
    -------

    """

    # Sum train and test together for now
    n_total = n_train + n_test

    # Calculate actual values for the number of the missing features
    n_features_to_drop_outcome_not_counfounders = math.floor(
        (n_features_outcome - n_confounders) * missing_data_scaler)
    n_features_to_drop_treatment_effect_not_counfounders = math.floor(
        (n_features_treatment_effect - n_confounders) * missing_data_scaler)
    n_features_to_drop_confounders = math.floor(
        n_confounders * missing_data_scaler)
    n_features_to_drop_propensity = math.floor(
        n_features_propensity * missing_data_scaler)

    # create empty dataframe
    modeling_df = pd.DataFrame()

    np.random.seed(seed)

    # Generate Age - we will add mean=70 and sd=30 later to avoid high influence of this variable
    modeling_df['age'] = normal(loc=0, scale=1, size=n_total)

    # Generate features with uniform distribution - will multiply to 10 later
    for i in range(0, uniform_dim):
        modeling_df['sdoh_' +
                    str(i)] = np.ceil(uniform(size=n_total) * 10) / 10

    # Generate features with bernoulli distribution
    binary_coefs = uniform(size=binary_dim)
    for i in range(0, binary_dim):
        binary_coef = binary_coefs[i]
        modeling_df['binary_flag_' +
                    str(i)] = binomial(n=1, p=binary_coef, size=n_total)

    # Generate features with normal distribution
    multivariate_df = pd.DataFrame(multivariate_normal(np.zeros(normal_dim),
                                                       np.diag(
                                                           np.ones(normal_dim)),
                                                       n_total),
                                   columns=['vector_' + str(i) for i in range(0, normal_dim)])
    modeling_df = pd.concat([modeling_df, multivariate_df], axis=1)

    # logging.debug shape of the feature set
    logging.debug('Dimentionality of the featureset before dropping any features: {}'.format(
        modeling_df.shape), end='\n\n')

    # Extract name of the features
    features = pd.Series(modeling_df.columns)

    # sample features for the confounders
    confounders_features = features.sample(n_confounders)
    logging.debug(f'confounders_features: {confounders_features.values}')
    # sample features for the outcomes
    outcome_features_not_confounders = features[~features.isin(confounders_features)].sample(
        n_features_outcome - n_confounders)
    outcome_features = pd.concat(
        [outcome_features_not_confounders, confounders_features])
    logging.debug(f'outcome_features: {outcome_features.values}')

    # sample features for the treatment effect
    treatment_effect_features_not_confounders = features[~features.isin(outcome_features)].sample(
        n_features_treatment_effect - n_confounders)
    treatment_effect_features = pd.concat(
        [treatment_effect_features_not_confounders, confounders_features])
    logging.debug(f'treatment_effect_features: {treatment_effect_features.values}')
    # sample features for the propensity score
    propensity_score_features = features.sample(n_features_propensity)
    logging.debug(f'propensity_score_features: {propensity_score_features.values}')

    # Generate coefficients
    beta_outcome = normal(0, 1, n_features_outcome)
    top_outcome_features = pd.DataFrame(
        {'outcome_features': outcome_features, 'beta_coef': np.abs(beta_outcome)}).sort_values(
        by='beta_coef', ascending=False).reset_index(drop=True).head(5)['outcome_features'].values
    logging.debug(f'Top outcome_features by descending importance: {top_outcome_features}')

    # Generate outcomes
    modeling_df['y0'] = np.dot(modeling_df[outcome_features], beta_outcome) + normal(0,
                                                                                     outcome_noise_sd)

    # Generate coefficients
    beta_te = normal(0, 1, n_features_treatment_effect)
    top_treatment_effect = pd.DataFrame({'treatment_effect_features': treatment_effect_features,
                                         'beta_coef': np.abs(beta_te)}).sort_values(by='beta_coef',
                                                                                    ascending=False).reset_index(
        drop=True).head(5)['treatment_effect_features'].values
    logging.debug(f'Top treatment_effect_features by descending importance: {top_treatment_effect}')

    # Generate outcomes
    modeling_df['true_ite'] = np.dot(
        modeling_df[treatment_effect_features], beta_te)

    # Generate coefficients for propensity score
    # Draw coefficients from beta distributions
    beta_propensity_score = normal(0, 1, n_features_propensity)

    top_propensity_score = pd.DataFrame({'propensity_score_features': propensity_score_features,
                                         'beta_coef': np.abs(beta_propensity_score)}).sort_values(
        by='beta_coef',
        ascending=False).reset_index(
        drop=True).head(5)['propensity_score_features'].values
    logging.debug(f'Top propensity_score_features by descending importance: {top_propensity_score}')

    # Generate propensity score and rescale it again from 0 to 1
    modeling_df['true_treatment_propensity'] = np.dot(modeling_df[propensity_score_features],
                                                      beta_propensity_score)

    # Center the distribution first
    modeling_df['true_treatment_propensity'] = modeling_df['true_treatment_propensity'] - \
                                               modeling_df['true_treatment_propensity'].mean()

    # Rescale to -1 to +1
    modeling_df['true_treatment_propensity'] = modeling_df['true_treatment_propensity'] / \
                                               modeling_df['true_treatment_propensity'].abs().max()

    # Rescale to get treatment_share_scaler
    modeling_df['true_treatment_propensity'] = modeling_df['true_treatment_propensity'] * \
                                               min(treatment_share_scaler,
                                                   1 - treatment_share_scaler)

    # Move to the right
    modeling_df['true_treatment_propensity'] = modeling_df['true_treatment_propensity'] + \
                                               treatment_share_scaler

    logging.debug('Average true_treatment_propensity value:{:0.2f}'.format(
        modeling_df['true_treatment_propensity'].mean()))
    logging.debug('Min true_treatment_propensity value:{:0.2f}'.format(
        modeling_df['true_treatment_propensity'].min()))
    logging.debug('Max true_treatment_propensity value:{:0.2f}'.format(
        modeling_df['true_treatment_propensity'].max()), end='\n\n')

    # If binary - use propensity score to generate bernoulli treatment
    # If continuous - just rescale propensity score

    # # Rescale to the needed distribution - shift mean to zero, then shift to all by treatment_share_scaler
    # modeling_df['true_treatment_propensity'] = (
    #     modeling_df['true_treatment_propensity'] - modeling_df['true_treatment_propensity'].mean()) + treatment_share_scaler

    if binary_treatment:
        modeling_df['treatment'] = binomial(n=1, p=modeling_df['true_treatment_propensity'],
                                            size=n_total)
    else:
        modeling_df['treatment'] = modeling_df['true_treatment_propensity']

    logging.debug('Average treatment value:{:0.2f}'.format(
        modeling_df['treatment'].mean()))
    logging.debug('Min treatment value:{:0.2f}'.format(modeling_df['treatment'].min()))
    logging.debug('Max treatment value:{:0.2f}'.format(
        modeling_df['treatment'].max()), end='\n\n')

    modeling_df['y1'] = modeling_df['y0'] + modeling_df['true_ite']
    modeling_df['y'] = modeling_df['y0'] + \
                       modeling_df['true_ite'] * modeling_df['treatment']

    # Rescale from 0 to 1
    y_min = modeling_df[['y', 'y0', 'y1']].min().min()
    y_max = modeling_df[['y', 'y0', 'y1']].max().max()
    scale_factor = 1 / (y_max - y_min)
    modeling_df['y'] = (modeling_df['y'] - y_min) * scale_factor
    modeling_df['y0'] = (modeling_df['y0'] - y_min) * scale_factor
    modeling_df['y1'] = (modeling_df['y1'] - y_min) * scale_factor

    modeling_df['true_ite_rescaled'] = modeling_df['true_ite'] * scale_factor
    modeling_df['true_ite'] = modeling_df['y1'] - \
                              modeling_df['y0']  # modeling_df['true_ite'] * scale_factor

    logging.debug('Average treatment effect value:{:0.2f}'.format(
        modeling_df['true_ite'].mean()))
    logging.debug('Min treatment effect value:{:0.2f}'.format(
        modeling_df['true_ite'].min()))
    logging.debug('Max treatment effect value:{:0.2f}'.format(
        modeling_df['true_ite'].max()), end='\n\n')

    # If binary - rescale to [0,1] and use as probability to generate bernoulli outcome
    if binary_outcome:
        modeling_df['y'] = binomial(n=1, p=modeling_df['y'], size=n_total)

    logging.debug('Average outcome value:{:0.2f}'.format(modeling_df['y'].mean()))
    logging.debug('Min outcome value:{:0.2f}'.format(modeling_df['y'].min()))
    logging.debug('Max outcome value:{:0.2f}'.format(
        modeling_df['y'].max()), end='\n\n')

    # drop temporary variables
    #    del modeling_df['y0']

    # Rescale age feature
    modeling_df['age'] = np.where(modeling_df['age'] * 30 + 70 < 50, 50,
                                  modeling_df['age'] * 30 + 70)

    # Rescale SDOH features
    for i in range(0, uniform_dim):
        modeling_df['sdoh_' + str(i)] = modeling_df['sdoh_' + str(i)] * 10

    # features_to_drop_outcome_not_counfounders
    features_to_drop_outcome_not_counfounders = outcome_features_not_confounders.sample(
        n_features_to_drop_outcome_not_counfounders)
    logging.debug(
        f'n_features_to_drop_outcome_not_counfounders: {n_features_to_drop_outcome_not_counfounders}')
    logging.debug(
        f'features_to_drop_outcome_not_counfounders: {features_to_drop_outcome_not_counfounders.values}')

    # features_to_drop_treatment_effect_not_confounders
    features_to_drop_treatment_effect_not_confounders = treatment_effect_features_not_confounders.sample(
        n_features_to_drop_treatment_effect_not_counfounders)
    logging.debug(
        f'n_features_to_drop_treatment_effect_not_counfounders: {n_features_to_drop_treatment_effect_not_counfounders}')
    logging.debug(
        f'features_to_drop_treatment_effect_not_confounders: {features_to_drop_treatment_effect_not_confounders.values}')

    # features_to_drop_confounders
    features_to_drop_confounders = confounders_features.sample(
        n_features_to_drop_confounders)
    logging.debug(f'n_features_to_drop_confounders: {n_features_to_drop_confounders}')
    logging.debug(f'features_to_drop_confounders: {features_to_drop_confounders.values}')

    # features_to_drop_confounders
    features_to_drop_propensity = propensity_score_features.sample(
        n_features_to_drop_propensity)
    logging.debug(f'n_features_to_drop_propensity: {n_features_to_drop_propensity}')
    logging.debug(f'features_to_drop_propensity: {features_to_drop_propensity.values}')

    # Now drop all those features
    all_features_to_drop = pd.concat([features_to_drop_outcome_not_counfounders,
                                      features_to_drop_treatment_effect_not_confounders,
                                      features_to_drop_confounders,
                                      features_to_drop_propensity]).drop_duplicates()

    for col in all_features_to_drop:
        logging.debug('Dropping {} from the columns'.format([col]))
        assert (col in modeling_df), 'All features to drop should be in the featureset'
        del modeling_df[col]

    # Randomly select train and test
    y = modeling_df['y']
    t = modeling_df['treatment']
    true_ite = modeling_df['true_ite']
    true_treatment_propensity = modeling_df['true_treatment_propensity']
    X = modeling_df.drop(['y', 'y0', 'y1', 'treatment', 'true_ite',
                          'true_treatment_propensity', 'true_ite_rescaled'], axis=1)

    # train_test_split
    logging.debug('Split to train ({} records) and test ({} records)'.format(n_train, n_test))
    X_train, X_test, t_train, t_test, y_train, y_test, true_ite_train, true_ite_test, true_treatment_propensity_train, true_treatment_propensity_test = train_test_split(
        X, t, y, true_ite, true_treatment_propensity, test_size=n_test,
        train_size=n_train, random_state=42)
    return (X_train, X_test, t_train, t_test, y_train, y_test, true_ite_train, true_ite_test,
            true_treatment_propensity_train, true_treatment_propensity_test)
