TFile *f;
TTree *t;
TH2F *h, *h2, *h3;
TCanvas *c;


void analyse_time_slice(const char *filename)
{
	f = new TFile(filename);
	assert(f);
	t = (TTree *)f->Get("tree");
	assert(t);

	double time;
	float energy;
	float posx;
	Int_t id1;
	Int_t id2;

	t->SetBranchAddress("energy", &energy);
	t->SetBranchAddress("time", &time);
	t->SetBranchAddress("globalPosX", &posx);
	t->SetBranchAddress("level1ID", &id1);
	t->SetBranchAddress("level2ID", &id2);

	int entries = t->GetEntries();

	int n_crystals = 32;

	h = new TH2F("posx/time", "posx/time", 10, 0, 1, 1000, -1000, 1000);
	h2 = new TH2F("id1/time", "id1/time", 10, 0, 1, 2, 0, 2);
	h3 = new TH2F("id2/time", "id2/time", 10, 0, 1, n_crystals, 0, n_crystals);

	for (int i = 0; i < entries; ++i) {
		t->GetEntry(i);
		h->Fill(time, -posx);
		h2->Fill(time, id1);
		if (id1 == 1) {
			h3->Fill(time, id2);
		}
	}

	c = new TCanvas("output", "output");
	c->Divide(2,2);

	c->cd(1);
	gPad->SetLogz();
	h->Draw("colz");
	c->cd(2);
	h2->Draw("colz");
	c->cd(3);
	h3->Draw("colz");
}
