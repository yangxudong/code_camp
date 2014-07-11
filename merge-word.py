#!/usr/bin/python
import sys, getopt
from heapq import heappush, heappop

def usage(prog):
  print '%s --alpha <alpha_value> --product <product_file> --word2vec <word2vec_file> --click <click_file>' % prog

def load(filename):
  content = set()
  file_object = open(filename)
  for line in file_object:
    content.add(line.rstrip())
  file_object.close()
  return content

def load_click_data(filename, products):
  content = {}
  file_object = open(filename)
  for line in file_object:
    fields = line.rstrip().split('\t')
    if len(fields) < 3: continue
    word = fields[1]
    elements = fields[2].split(':')
    max_click = float(elements[1])
    #delta = max_click / 2
    dict_w = {}
    if elements[0] != word:
      dict_w[elements[0]] = 1.0
    for i in range(2, len(fields)):
      elements = fields[i].split(':')
      if elements[0] == word: continue
      click = float(elements[1])
      if elements[0] in products:
        #click += delta
        click *= 2
      dict_w[elements[0]] = 0.99 if click >= max_click else click / max_click
    content[word] = dict_w
  file_object.close()
  return content

if __name__ == '__main__':
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'a:p:w:c:h', ['product=', 'word2vec=', 'click=', 'alpha=', 'help'])
  except getopt.GetoptError:
    print >>sys.stderr, "[ERROR]\tIllegal input parameters format!"
    usage(sys.argv[0])
    sys.exit(1)
  alpha = 0.7
  for opt_k, opt_v in opts:
    if opt_k in ('--product', '-p'):
      products = load(opt_v)
    if opt_k in ('--word2vec', '-w'):
      word2vec = opt_v
    if opt_k in ('--click', '-c'):
      click_file = opt_v
    if opt_k in ('--alpha', '-a'):
      alpha = float(opt_v)
    if opt_k in ('--help', '-h'):
      usage(sys.argv[0])
      sys.exit(0)

  if not click_file or not word2vec:
    usage(sys.argv[0])
    sys.exit(0)

  click = load_click_data(click_file, products)
  float_f = lambda (c, w): '%s:%f' % (w, -c)

  file_object = open(word2vec)
  for line in file_object:
    fields = line.rstrip().split('')
    word = fields[0]
    if word not in click:
      print ''.join([word, '\t'.join(fields[1:])])
      continue
    word_list = []
    for i in range(1, len(fields)):
      elements = fields[i].split(':')
      if len(elements) < 2: continue
      click_score = click[word].pop(elements[0], 0)
      score = (1 - alpha) * float(elements[1]) + alpha * click_score
      #if word in products and elements[0] in products: score *= 1.1
      heappush(word_list, (-score, elements[0]))
    #if word in products:
    #  for w, s in click[word].iteritems():
    #    if not w in products: continue
    #    heappush(word_list, (-(1.1 * alpha * s), w))
    max_output_num = 100 if len(word_list) >= 100 else len(word_list)
    output_list = [ float_f(heappop(word_list)) for i in range(max_output_num) ]
    print ''.join([word, '\t'.join(output_list)])
  file_object.close()
