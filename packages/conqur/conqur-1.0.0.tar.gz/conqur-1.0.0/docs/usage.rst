=====
Usage
=====

To use ConQuR in a project::

    import conqur

Or just::

    from conqur import scaler

To create a model, use::

    model = scaler.ConQur(batch_columns, covariate_columns, reference_values, (some special arguments))

Then you should fit your model on the training data and transform the another matrix after fit::

    model.fit(X_1)
    model.tranform(X_2)

Or just::

    model.fit_transform(X)

if you need to transform the initial matrix.
