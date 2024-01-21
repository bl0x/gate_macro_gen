TFile *f, *fl, *fbg, *flbg;
TTree *t, *tl, *tbg, *tlbg;
TH2F *h1 , *h2 , *h3 , *h4 , *h5 , *h6 , *h7 , *h8,
     *h9 , *h10, *h11, *h12, *h13, *h14, *h15, *h16,
     *h17, *h18;
TH1F *hr, *he, *hle;
TCanvas *c;


void analyse_dual_energy(TString filename)
{
	f = new TFile(filename + ".Singles_crystal.root");
	assert(f);
	fl = new TFile(filename + ".Singles_crystal_le.root");
	assert(fl);
	fbg = new TFile(filename + "_bg.Singles_crystal.root");
	assert(fbg);
	flbg = new TFile(filename + "_bg.Singles_crystal_le.root");
	assert(flbg);
	t = (TTree *)f->Get("tree");
	assert(t);
	tl = (TTree *)fl->Get("tree");
	assert(tl);
	tbg = (TTree *)fbg->Get("tree");
	assert(tbg);
	tlbg = (TTree *)flbg->Get("tree");
	assert(tlbg);

	double time;
	float energy;
	float posx;
	Int_t id1;
	Int_t id2;

	double timel;
	float energyl;
	float posxl;
	Int_t id1l;
	Int_t id2l;

	double timebg;
	float energybg;
	float posxbg;
	Int_t id1bg;
	Int_t id2bg;

	double timelbg;
	float energylbg;
	float posxlbg;
	Int_t id1lbg;
	Int_t id2lbg;
	/*ULong64_t id1;
	ULong64_t id2;*/

	t->SetBranchAddress("energy", &energy);
	t->SetBranchAddress("time", &time);
	t->SetBranchAddress("globalPosX", &posx);
	t->SetBranchAddress("line_level1ID", &id1);
	t->SetBranchAddress("line_level2ID", &id2);

	tl->SetBranchAddress("energy", &energyl);
	tl->SetBranchAddress("time", &timel);
	tl->SetBranchAddress("globalPosX", &posxl);
	tl->SetBranchAddress("line_level1ID", &id1l);
	tl->SetBranchAddress("line_level2ID", &id2l);

	tbg->SetBranchAddress("energy", &energybg);
	tbg->SetBranchAddress("time", &timebg);
	tbg->SetBranchAddress("globalPosX", &posxbg);
	tbg->SetBranchAddress("line_level1ID", &id1bg);
	tbg->SetBranchAddress("line_level2ID", &id2bg);

	tlbg->SetBranchAddress("energy", &energylbg);
	tlbg->SetBranchAddress("time", &timelbg);
	tlbg->SetBranchAddress("globalPosX", &posxlbg);
	tlbg->SetBranchAddress("line_level1ID", &id1lbg);
	tlbg->SetBranchAddress("line_level2ID", &id2lbg);

	int entries = t->GetEntries();
	int entriesl = t->GetEntries();

	int entries_bg = tbg->GetEntries();
	int entriesl_bg = tlbg->GetEntries();

	assert(entries == entriesl);
	assert(entries_bg == entriesl_bg);

	const int n_crystals = 64;

	h1 = new TH2F("id2/time", "id2/time",
		20, 0, 1, n_crystals, 0, n_crystals);
	h2 = new TH2F("id2_bg/time", "id2_bg/time",
		20, 0, 1, n_crystals, 0, n_crystals);
	//h3 = new TH2F("id2/time", "id2/time",
	//	20, 0, 1, n_crystals, 0, n_crystals);
	h4 = new TH2F("id2_bg/time", "id2_bg/time",
		20, 0, 1, n_crystals, 0, n_crystals);
	h5 = new TH2F("id2_nobg/time", "id2_nobg/time",
		20, 0, 1, n_crystals, 0, n_crystals);
	//h6 = new TH2F("id2l/time", "id2l/time",
	//	20, 0, 1, n_crystals, 0, n_crystals);
	h7 = new TH2F("id2l_bg/time", "id2l_bg/time",
		20, 0, 1, n_crystals, 0, n_crystals);
	h8 = new TH2F("id2l_nobg/time", "id2l_nobg/time",
		20, 0, 1, n_crystals, 0, n_crystals);
	h9 = new TH2F("id2l_bg/time", "id2l_bg/time",
		20, 0, 1, n_crystals, 0, n_crystals);
	h10 = new TH2F("id2l_nobg/time", "id2l_nobg/time",
		20, 0, 1, n_crystals, 0, n_crystals);

	h11 = new TH2F("e/el", "e/el",
		20, 0, 1, n_crystals, 0, n_crystals);
	h12 = new TH2F("el/e", "el/e",
	    	20, 0, 1, n_crystals, 0, n_crystals);

	/*h4 = new TH2F("id2/time*e", "id2/time*e", 100, 0, 0.2, 100, 0, 10);
	h5 = new TH2F("id2/time*e", "id2/time*e", 100, 0, 0.2, 100, 0, 10);
	h6 = new TH2F("id2/time*e", "id2/time*e", 100, 0, 0.2, 100, 0, 10);*/

	he = new TH1F("HE", "HE", 100, 0, 0.2);
	hle = new TH1F("LE", "LE", 100, 0, 0.2);

	/* calculate background */
	for (int i = 0; i < entries_bg; ++i) {
		tbg->GetEntry(i);
		tlbg->GetEntry(i);
		if (id1bg == 1) {
			if (energybg > 0 && energylbg > 0) {
				h7->Fill(timebg, id2bg);
				h9->Fill(timebg, id2lbg);
				h2->Fill(timebg, id2bg, energybg);
				h5->Fill(timebg, id2lbg, energylbg);
			}
			if (id2bg == 60) {
				he->Fill(energybg);
			}
			if (id2lbg == 60) {
				hle->Fill(energylbg);
			}
		}
	}

	/* fill normal histograms */
	for (int i = 0; i < entries; ++i) {
		t->GetEntry(i);
		tl->GetEntry(i);
		if (id1 == 1) {
			/* printf("%d %d\n", id1, id2); */
			if (energy > 0 && energyl > 0) {
				h8->Fill(time, id2);
				h10->Fill(time, id2l);
				h1->Fill(time, id2, energy);
				h4->Fill(time, id2l, energyl);
				/*if (id2 > 6 && id2 < 10) {
					h4->Fill(energy, energy/energyl);
				}
				if (id2 > 10 && id2 < 20) {
					h5->Fill(energy, energy/energyl);
				}
				if (id2 > 22 && id2 < 30) {
					h6->Fill(energy, energy/energyl);
				}*/
			}
		}
	}

	/* subtract signal from background */
	h15 = (TH2F *)h2->Clone();
	h16 = (TH2F *)h5->Clone();
	//h3->Scale(0.2);
	//h6->Scale(0.2);
	h15->Add(h1, -1);
	h16->Add(h4, -1);

	/* divide background by signal */
	h3 = (TH2F *)h1->Clone("background/signal");
	h6 = (TH2F *)h4->Clone("background/signal_l");
	h3->Divide(h2);
	h6->Divide(h5);

	h11 = (TH2F *)h3->Clone("HE/LE");
	h12 = (TH2F *)h6->Clone("LE/HE");

	/* logarithm of histograms */
	for (int i = 0; i < h11->GetNbinsX(); ++i) {
		for (int j = 0; j < h11->GetNbinsY(); ++j) {
			h11->SetBinContent(i, j,
			    log(h11->GetBinContent(i, j)*100));
		}
	}
	for (int i = 0; i < h12->GetNbinsX(); ++i) {
		for (int j = 0; j < h12->GetNbinsY(); ++j) {
			h12->SetBinContent(i, j,
			    log(h12->GetBinContent(i, j)*100));
		}
	}

	h13 = (TH2F *)h11->Clone();
	h14 = (TH2F *)h12->Clone();
	h13->Divide(h12);
	h14->Divide(h11);

	h17 = (TH2F *)h15->Clone();
	h18 = (TH2F *)h16->Clone();
	h17->Divide(h16);
	h18->Divide(h15);

	int xmin = 11;
	int xmax = 12;
	int ymin[6] = {17, 25, 33, 42, 50, 58};
	int ymax[6] = {22, 30, 38, 47, 55, 63};

	hr = new TH1F("R", "R", 6, 0, 6);

	for (int i = 0; i < h17->GetNbinsX(); ++i) {
		for (int j = 0; j < h17->GetNbinsY(); ++j) {
			for (int n = 0; n < 7; ++n) {
				if (ymin[n] < j && j < ymax[n]) {
					hr->Fill(n, h17->GetBinContent(i, j));
				}
			}
		}
	}

	c = new TCanvas("output", "output");
	c->Divide(5,5);

	h7->SetTitle("counts HE bg");
	h8->SetTitle("counts HE");

	h1->SetTitle("current HE");
	h2->SetTitle("current HE bg");
	h3->SetTitle("current HE no bg (div)");
	h15->SetTitle("current HE no bg (sub)");

	h9->SetTitle("counts LE bg");
	h10->SetTitle("counts LE");

	h4->SetTitle("current LE");
	h5->SetTitle("current LE bg");
	h6->SetTitle("current LE no bg (div)");
	h16->SetTitle("current LE no bg (sub)");

	h11->SetTitle("log(current HE)");
	h12->SetTitle("log(current LE)");

	h13->SetTitle("log(HE)/log(LE)");
	h14->SetTitle("log(LE)/log(HE)");

	h17->SetTitle("HE/LE");
	h18->SetTitle("LE/HE");

	c->cd(1); h7->Draw("colz");
	c->cd(2); h8->Draw("colz");
	c->cd(3); h1->Draw("colz");
	c->cd(4); h2->Draw("colz");
	c->cd(5); h3->Draw("colz");
	c->cd(6); h9->Draw("colz");
	c->cd(7); h10->Draw("colz");
	c->cd(8); h4->Draw("colz");
	c->cd(9); h5->Draw("colz");
	c->cd(10); h6->Draw("colz");
	c->cd(11); h11->Draw("colz");
	c->cd(12); h12->Draw("colz");
	c->cd(13); h13->Draw("colz");
	c->cd(14); h14->Draw("colz");
	c->cd(15); h15->Draw("colz");
	c->cd(16); h16->Draw("colz");
	c->cd(17); h17->Draw("colz");
	c->cd(18); h18->Draw("colz");
	c->cd(19); hr->Draw();
	c->cd(21); he->Draw();
	c->cd(22); hle->Draw();
}
