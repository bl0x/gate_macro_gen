void get_tube_spectrum(TString filename, float e_MeV)
{
	TFile *f = new TFile(filename);
	assert(f);

	TTree *t = (TTree *)f->Get("Singles");

	int bins = 200;

	TH1F *h = new TH1F("e", Form("E = %d keV", (int)round(e_MeV * 1e3)),
	    bins, 0, e_MeV*1.1);

	Float_t energy;
	Double_t time;
	int n;

	float t_thr = 2.1e-9;

	t->SetBranchAddress("time", &time);
	t->SetBranchAddress("energy", &energy);

	n = t->GetEntries();

	for (int i = 0; i < n; ++i) {
		t->GetEntry(i);

		if (time < t_thr) {
			h->Fill(energy);
		}
	}

	FILE *out = fopen("/tmp/hist", "w");
	assert(out);

	fprintf(out, "%s",
	    Form("## Interpolated x-ray tube spectrum, E = %d keV\n",
		    (int)round(e_MeV * 1e3)));
	fprintf(out, "## file: %s\n", filename.Data());
	fprintf(out, "3 0\n");
	for (int i = 0; i < bins; ++i) {
		float c = h->GetBinCenter(i);
		if (c >= 0) {
		fprintf(out, "%f %f\n", c,
		    h->GetBinContent(i));
		}
	}
	fclose(out);
	h->Draw();
}
