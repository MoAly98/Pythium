# Prototype config
from slimming_classes import Sample
tH_sample = Sample('tHq', {XXXX: ['/somewhere/on/eos/mc16a/', '/somewhere/on/eos/mc16d/'], YYYYY: ['/somewhere_else/on/eos/mc16a/', '/somewhere_else/on/eos/mc16d/']}, trees_to_branches = {'nominal_loose':[('bdt_tH','on'), ('bdt_ttb','off')], 'SystTree':[('bdt_tH',1), ('bdt_ttb',0)]})