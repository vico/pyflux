import numpy as np
import pyflux as pf

noise = np.random.normal(0,0.1,100)
data = np.zeros(100)

for i in range(1,len(data)):
    data[i] = 0.9*data[i-1] + noise[i]

data = np.random.poisson(np.exp(data),100)

def test_no_terms():
    """
    Tests an ARIMA model with no AR or MA terms, and that
    the latent variable list length is correct, and that the estimated
    latent variables are not nan
    """
    model = pf.ARIMA(data=data, ar=0, ma=0, family=pf.Poisson())
    x = model.fit()
    assert(len(model.latent_variables.z_list) == 1)
    lvs = np.array([i.value for i in model.latent_variables.z_list])
    assert(len(lvs[np.isnan(lvs)]) == 0)

def test_couple_terms():
    """
    Tests an ARIMA model with 1 AR and 1 MA term and that
    the latent variable list length is correct, and that the estimated
    latent variables are not nan
    """
    model = pf.ARIMA(data=data, ar=1, ma=1, family=pf.Poisson())
    x = model.fit()
    assert(len(model.latent_variables.z_list) == 3)
    lvs = np.array([i.value for i in model.latent_variables.z_list])
    assert(len(lvs[np.isnan(lvs)]) == 0)

def test_bbvi():
    """
    Tests an ARIMA model estimated with BBVI and that the length of the latent variable
    list is correct, and that the estimated latent variables are not nan
    """
    model = pf.ARIMA(data=data, ar=1, ma=1, family=pf.Poisson())
    x = model.fit('BBVI',iterations=100)
    assert(len(model.latent_variables.z_list) == 3)
    lvs = np.array([i.value for i in model.latent_variables.z_list])
    assert(len(lvs[np.isnan(lvs)]) == 0)

def test_bbvi_mini_batch():
    """
    Tests an ARIMA model estimated with BBVI and that the length of the latent variable
    list is correct, and that the estimated latent variables are not nan
    """
    model = pf.ARIMA(data=data, ar=1, ma=1, family=pf.Poisson())
    x = model.fit('BBVI',iterations=100, mini_batch=32)
    assert(len(model.latent_variables.z_list) == 3)
    lvs = np.array([i.value for i in model.latent_variables.z_list])
    assert(len(lvs[np.isnan(lvs)]) == 0)

def test_bbvi_elbo():
    """
    Tests that the ELBO increases
    """
    model = pf.ARIMA(data=data, ar=1, ma=1, family=pf.Poisson())
    x = model.fit('BBVI',iterations=100, record_elbo=True)
    assert(x.elbo_records[-1]>x.elbo_records[0])

def test_bbvi_mini_batch_elbo():
    """
    Tests that the ELBO increases
    """
    model = pf.ARIMA(data=data, ar=1, ma=1, family=pf.Poisson())
    x = model.fit('BBVI',iterations=100, mini_batch=32, record_elbo=True)
    assert(x.elbo_records[-1]>x.elbo_records[0])

def test_mh():
    """
    Tests an ARIMA model estimated with Metropolis-Hastings and that the length of the 
    latent variable list is correct, and that the estimated latent variables are not nan
    """
    model = pf.ARIMA(data=data, ar=1, ma=1, family=pf.Poisson())
    x = model.fit('M-H',nsims=300)
    assert(len(model.latent_variables.z_list) == 3)
    lvs = np.array([i.value for i in model.latent_variables.z_list])
    assert(len(lvs[np.isnan(lvs)]) == 0)

def test_laplace():
    """
    Tests an ARIMA model estimated with Laplace approximation and that the length of the 
    latent variable list is correct, and that the estimated latent variables are not nan
    """
    model = pf.ARIMA(data=data, ar=1, ma=1, family=pf.Poisson())
    x = model.fit('Laplace')
    assert(len(model.latent_variables.z_list) == 3)
    lvs = np.array([i.value for i in model.latent_variables.z_list])
    assert(len(lvs[np.isnan(lvs)]) == 0)

def test_pml():
    """
    Tests a PML model estimated with Laplace approximation and that the length of the 
    latent variable list is correct, and that the estimated latent variables are not nan
    """
    model = pf.ARIMA(data=data, ar=1, ma=1, family=pf.Poisson())
    x = model.fit('PML')
    assert(len(model.latent_variables.z_list) == 3)
    lvs = np.array([i.value for i in model.latent_variables.z_list])
    assert(len(lvs[np.isnan(lvs)]) == 0)

def test_predict_length():
    """
    Tests that the prediction dataframe length is equal to the number of steps h
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit()
    assert(model.predict(h=5).shape[0] == 5)

def test_predict_is_length():
    """
    Tests that the prediction IS dataframe length is equal to the number of steps h
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit()
    assert(model.predict_is(h=5).shape[0] == 5)

def test_predict_nans():
    """
    Tests that the predictions are not nans
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit()
    assert(len(model.predict(h=5).values[np.isnan(model.predict(h=5).values)]) == 0)

def test_predict_is_nans():
    """
    Tests that the in-sample predictions are not nans
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit()
    assert(len(model.predict_is(h=5).values[np.isnan(model.predict_is(h=5).values)]) == 0)

def test_predict_nonconstant():
    """
    We should not really have predictions that are constant (should be some difference)...
    This captures bugs with the predict function not iterating forward
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit()
    predictions = model.predict(h=10, intervals=False)
    assert(not np.all(predictions.values==predictions.values[0]))
    
def test_predict_is_nonconstant():
    """
    We should not really have predictions that are constant (should be some difference)...
    This captures bugs with the predict function not iterating forward
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit()
    predictions = model.predict_is(h=10, intervals=False)
    assert(not np.all(predictions.values==predictions.values[0]))
    
def test_predict_intervals():
    """
    Tests prediction intervals are ordered correctly
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit()
    predictions = model.predict(h=10, intervals=True)

    assert(np.all(predictions['99% Prediction Interval'].values >= predictions['95% Prediction Interval'].values))
    assert(np.all(predictions['95% Prediction Interval'].values >= predictions['5% Prediction Interval'].values))
    assert(np.all(predictions['5% Prediction Interval'].values >= predictions['1% Prediction Interval'].values))


def test_predict_is_intervals():
    """
    Tests prediction intervals are ordered correctly
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit()
    predictions = model.predict_is(h=10, intervals=True)
    print(predictions)
    assert(np.all(predictions['99% Prediction Interval'].values >= predictions['95% Prediction Interval'].values))
    assert(np.all(predictions['95% Prediction Interval'].values >= predictions['5% Prediction Interval'].values))
    assert(np.all(predictions['5% Prediction Interval'].values >= predictions['1% Prediction Interval'].values))


def test_predict_intervals_bbvi():
    """
    Tests prediction intervals are ordered correctly
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit('BBVI', iterations=100)
    predictions = model.predict(h=10, intervals=True)

    assert(np.all(predictions['99% Prediction Interval'].values >= predictions['95% Prediction Interval'].values))
    assert(np.all(predictions['95% Prediction Interval'].values >= predictions['5% Prediction Interval'].values))
    assert(np.all(predictions['5% Prediction Interval'].values >= predictions['1% Prediction Interval'].values))


def test_predict_is_intervals_bbvi():
    """
    Tests prediction intervals are ordered correctly
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit('BBVI', iterations=100)
    predictions = model.predict_is(h=10, intervals=True)
    assert(np.all(predictions['99% Prediction Interval'].values >= predictions['95% Prediction Interval'].values))
    assert(np.all(predictions['95% Prediction Interval'].values >= predictions['5% Prediction Interval'].values))
    assert(np.all(predictions['5% Prediction Interval'].values >= predictions['1% Prediction Interval'].values))


def test_predict_intervals_mh():
    """
    Tests prediction intervals are ordered correctly
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit('M-H', nsims=400)
    predictions = model.predict(h=10, intervals=True)
    assert(np.all(predictions['99% Prediction Interval'].values >= predictions['95% Prediction Interval'].values))
    assert(np.all(predictions['95% Prediction Interval'].values >= predictions['5% Prediction Interval'].values))
    assert(np.all(predictions['5% Prediction Interval'].values >= predictions['1% Prediction Interval'].values))

def test_predict_is_intervals_mh():
    """
    Tests prediction intervals are ordered correctly
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit('M-H', nsims=400)
    predictions = model.predict_is(h=10, intervals=True)
    assert(np.all(predictions['99% Prediction Interval'].values >= predictions['95% Prediction Interval'].values))
    assert(np.all(predictions['95% Prediction Interval'].values >= predictions['5% Prediction Interval'].values))
    assert(np.all(predictions['5% Prediction Interval'].values >= predictions['1% Prediction Interval'].values))

def test_sample_model():
    """
    Tests sampling function
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit('BBVI', iterations=100)
    sample = model.sample(nsims=100)
    assert(sample.shape[0]==100)
    assert(sample.shape[1]==len(data)-2)

def test_ppc():
    """
    Tests PPC value
    """
    model = pf.ARIMA(data=data, ar=2, ma=2, family=pf.Poisson())
    x = model.fit('BBVI', iterations=100)
    p_value = model.ppc(nsims=100)
    assert(0.0 <= p_value <= 1.0)
