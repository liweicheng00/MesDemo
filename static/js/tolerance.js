const calculate_tol = function(condition, if_true, if_false) {
	function a(val) {
	console.log(val)
		if (typeof(val) == 'undefined') {
			return null
		}
		if (val == '-') {
			val = null
		}
		if (condition == null) {
			return {
				tol: '-',
				max: '-',
				min: '-',
			}
		}
		// 無條件，只有上下限
		if (condition == 'no') {
			return {
				tol: '-',
				max: if_true, // 最大值
				min: if_false // 最小值
			}
		}
		var tol = (val >= condition) ? if_true : if_false
		var str_tol = ''
		if (tol < 1) {
			str_tol = "±" + tol * 100 + "%"
		} else {
			str_tol = "±" + tol
		}
		return {
			tol: str_tol,
			max: (tol == if_true) ? (val * (1 + if_true)).toFixed(2) : val + tol,
			min: (((tol == if_true) ? val * (1 - if_true) : val - tol) > 0) ? ((tol == if_true) ? (val * (1 - if_true)).toFixed(
				2) : val - tol) : 0,
		}
	}
	return a

}
const tolerance = {
	NowTn2: calculate_tol(0, 0.05, null),
	NowT1: calculate_tol(0, 0.05, null),
	NowT2: calculate_tol(0, 0.05, null),
	NowT3: calculate_tol(0, 0.05, null),
	NowT4: calculate_tol(0, 0.05, null),
	Tn2: calculate_tol(0, 0.05, null),
	T1: calculate_tol(0, 0.05, null),
	T2: calculate_tol(0, 0.05, null),
	T3: calculate_tol(0, 0.05, null),
	T4: calculate_tol(0, 0.05, null),
	ChrSpd3: calculate_tol(0, 0.1, null),
	ChrPrs3: calculate_tol(0, 0.2, null),
	ChrPos4: calculate_tol(0, 0.1, null),
	'ChrPos4-ChrPos3': calculate_tol(NaN, null, 4),
	InjPos0: calculate_tol(20, 0.15, 3),
	InjPos1: calculate_tol(20, 0.15, 3),
	InjPos2: calculate_tol(20, 0.15, 3),
	InjPos3: calculate_tol(20, 0.2, 3),
	InjPos4: calculate_tol(20, 0.2, 3),
	InjSpd0: calculate_tol(30, 0.2, 5),
	InjSpd1: calculate_tol(30, 0.2, 5),
	InjSpd2: calculate_tol(30, 0.2, 5),
	InjSpd3: calculate_tol(30, 0.2, 5),
	InjSpd4: calculate_tol(30, 0.2, 5),
	InjPrs0: calculate_tol(30, 0.1, 5),
	InjPrs1: calculate_tol(30, 0.1, 5),
	InjPrs2: calculate_tol(30, 0.1, 5),
	InjPrs3: calculate_tol(30, 0.1, 5),
	InjPrs4: calculate_tol(30, 0.1, 5),
	InjPos4: calculate_tol(NaN, null, 4),
	// InjPrs4: calculate_tol(0, 0.1, null),
	TtimeInjP: calculate_tol(NaN, null, 3),
	HldPrs0: calculate_tol(0, 0.2, null),
	HldPrs1: calculate_tol(0, 0.2, null),
	HldPrs2: calculate_tol(0, 0.2, null),
	HldPrs3: calculate_tol(0, 0.2, null),
	HldTime0: calculate_tol(NaN, null, 3),
	HldTime1: calculate_tol(NaN, null, 3),
	HldTime2: calculate_tol(NaN, null, 3),
	HldTime3: calculate_tol(NaN, null, 3),
	TimeDchr: calculate_tol(NaN, null, 3),
	BfCstTime: calculate_tol(NaN, null, 3),
	EjtPos3: calculate_tol(null, null, null),
	EjtSpd3: calculate_tol(null, null, null),
	EjtPrs3: calculate_tol(null, null, null),
	EjtPos0: calculate_tol(null, null, null),
	EjtSpd0: calculate_tol(null, null, null),
	EjtPrs0: calculate_tol(null, null, null),
	MopPos3: calculate_tol(null, null, null),
	MopPrs3: calculate_tol(null, null, null),
	MclPos5: calculate_tol(null, null, null),
	MclPos4: calculate_tol(null, null, null),
	MclPrs4: calculate_tol(null, null, null),
	TimeLpr: calculate_tol(null, null, null),

	DryTemp: calculate_tol(NaN, null, 5),
	DryTime: calculate_tol(null, null, null),
	DewPoint: calculate_tol('no', -5, -50),
	OilTemp: calculate_tol('no', 50, 0),
	MoTnMale: calculate_tol(NaN, null, 5),
	MoTnFemale: calculate_tol(NaN, null, 5),
	MoSlider: calculate_tol(NaN, null, 5),
	Plate: calculate_tol(NaN, null, 5),
	HtRunT1: calculate_tol(0, 0.05, null),
	HtRunT2: calculate_tol(0, 0.05, null),
	HtRunT3: calculate_tol(0, 0.05, null),
	HtRunT4: calculate_tol(0, 0.05, null),
	HtRunT5: calculate_tol(0, 0.05, null),
	HtRunT6: calculate_tol(0, 0.05, null),
	HtRunT7: calculate_tol(0, 0.05, null),
	HtRunT8: calculate_tol(0, 0.05, null),
	HtRunT9: calculate_tol(0, 0.05, null),
	HtRunT10: calculate_tol(0, 0.05, null),
	HtRunT11: calculate_tol(0, 0.05, null),
	HtRunT12: calculate_tol(0, 0.05, null),
	HtRunT13: calculate_tol(0, 0.05, null),
	HtRunT14: calculate_tol(0, 0.05, null),
	HtRunT15: calculate_tol(0, 0.05, null),
	ClmFrc: calculate_tol(null, null, null),
	ProdWeight: calculate_tol(null, null, null),
	FeederWeight: calculate_tol(null, null, null),
	CnsmptPH: calculate_tol(null, null, null)
}
const ParamChiName = {
	NowTn2: '(噴嘴)N1',
	NowT1: '(第一段)T1',
	NowT2: '(第二段)T2',
	NowT3: '(第三段)T3',
	NowT4: '(第四段)T4',
	ChrSpd3: '螺杆轉速',
	ChrPrs3: '背壓',
	ChrPos4: '計量',
	'ChrPos4-ChrPos3': '鬆退行程',
	InjPos0: '射一(NN機為S4)',
	InjPos1: '射二(NN機為S5)',
	InjPos2: '射三(NN機為S6)',
	InjPos3: '射四',
	InjPos4: '射五',
	InjSpd0: '中文名',
	InjSpd1: '中文名',
	InjSpd2: '中文名',
	InjSpd3: '中文名',
	InjSpd4: '中文名',
	InjPrs0: '中文名',
	InjPrs1: '中文名',
	InjPrs2: '中文名',
	InjPrs3: '中文名',
	InjPrs4: '中文名',
	// InjPos4: '中文名', // 重複
	// InjPrs4: '中文名', // 重複
	TtimeInjP: '中文名',
	HldPrs0: '中文名',
	HldPrs1: '中文名',
	HldPrs2: '中文名',
	HldPrs3: '中文名',
	HldTime0: '中文名',
	HldTime1: '中文名',
	HldTime2: '中文名',
	HldTime3: '中文名',
	TimeDchr: '中文名',
	BfCstTime: '中文名',
}
const Params = {
	DryTemp: '乾燥溫度',
	DryTime: '乾燥時間',
	DewPoint: '露點',
	OilTemp: '油溫',
	MoTnMale: '公模',
	MoTnFemale: '母模',
	MoSlider: '滑塊',
	Plate: '撥料版',
	HtRunT1: '熱膠道T1',
	HtRunT2: '熱膠道T2',
	HtRunT3: '熱膠道T3',
	HtRunT4: '熱膠道T4',
	HtRunT5: '熱膠道T5',
	HtRunT6: '熱膠道T6',
	HtRunT7: '熱膠道T7',
	HtRunT8: '熱膠道T8',
	HtRunT9: '熱膠道T9',
	HtRunT10: '熱膠道10T',
	HtRunT11: '熱膠道11T',
	HtRunT12: '熱膠道12T',
	HtRunT13: '熱膠道13T',
	HtRunT14: '熱膠道14T',
	HtRunT15: '熱膠道15T',
}
