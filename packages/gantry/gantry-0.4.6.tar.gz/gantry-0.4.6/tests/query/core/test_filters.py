from gantry.query.core.dataframe import Filters, _FilterObj


def test_and(series_obj):
    f1 = Filters([_FilterObj({"foo": "bar"}, series_obj)])
    f2 = Filters([_FilterObj({"bar": "baz"}, series_obj)])

    f_and = f1 & f2

    assert [f.filter_ for f in f_and.filter_objs] == [{"foo": "bar"}, {"bar": "baz"}]
    assert f_and.filter_objs[0].series is series_obj
    assert f_and.filter_objs[1].series is series_obj


def test_from_single_filter(series_obj):
    filter_ = Filters._from_single_filter({"foo": "bar"}, series_obj)
    assert [f.filter_ for f in filter_.filter_objs] == [{"foo": "bar"}]
    assert filter_.filter_objs[0].series is series_obj
