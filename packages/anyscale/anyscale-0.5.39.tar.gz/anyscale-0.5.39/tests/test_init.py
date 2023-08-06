def test_anyscale_base_import():
    import anyscale

    # Outputs should work with only base import
    anyscale.job.output({})
