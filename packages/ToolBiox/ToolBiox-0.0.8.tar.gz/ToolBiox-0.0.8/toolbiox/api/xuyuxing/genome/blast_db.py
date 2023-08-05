import gzip
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class BlastQuery(Base):
    __tablename__ = 'Query'

    num = Column(Integer, primary_key=True)
    qID = Column(String)
    qDef = Column(String)
    qLen = Column(Integer)

    def __repr__(self):
        return "<BlastQuery(ID='%d', query_name='%s')>" % (
            self.num, self.qDef)


class BlastHit(Base):
    __tablename__ = 'Hit'

    hit_num = Column(Integer, primary_key=True)
    query_num = Column(Integer, ForeignKey('Query.num'))
    hit_def = Column(String)
    hit_accession = Column(String)
    hit_len = Column(Integer)

    query = relationship("BlastQuery", back_populates="hit")

    def __repr__(self):
        return "<BlastHit(hit_num='%d', hit_name='%s')>" % (
            self.hit_num, self.hit_def)


BlastQuery.hit = relationship(
    "BlastHit", order_by=BlastHit.hit_num, back_populates="query")


class BlastHsp(Base):
    __tablename__ = 'Hsp'

    hsp_num = Column(Integer, primary_key=True)
    hit_num = Column(Integer, ForeignKey('Hit.hit_num'))
    query_num = Column(Integer, ForeignKey('Query.num'))
    hsp_bit_score = Column(Float)
    hsp_score = Column(Integer)
    hsp_evalue = Column(Float)
    hsp_query_from = Column(Integer)
    hsp_query_to = Column(Integer)
    hsp_hit_from = Column(Integer)
    hsp_hit_to = Column(Integer)
    hsp_query_frame = Column(Integer)
    hsp_hit_frame = Column(Integer)
    hsp_identity = Column(Float)
    hsp_positive = Column(Float)
    hsp_gaps = Column(Integer)
    hsp_align_len = Column(Integer)
    hsp_qseq = Column(String)
    hsp_hseq = Column(String)
    hsp_midline = Column(String)
    hsp_mismatch = Column(Integer)

    query = relationship("BlastQuery", back_populates="hsp")
    hit = relationship("BlastHit", back_populates="hsp")

    def __repr__(self):
        return "<BlastHsp(hsp_num='%d', hsp_bit_score='%f')>" % (
            self.hsp_num, self.hsp_bit_score)


BlastHit.hsp = relationship(
    "BlastHsp", order_by=BlastHsp.hsp_num, back_populates="hit")

BlastQuery.hsp = relationship(
    "BlastHsp", order_by=BlastHsp.hsp_num, back_populates="query")


def outfmt6_read_big(input_file, gzip_flag=False, query_num_start=0, hit_num_start=0, hsp_num_start=0):
    fieldname = ["q_id", "s_id", "identity", "aln_len", "mis", "gap", "q_start", "q_end", "s_start", "s_end", "e_value",
                 "score"]

    if gzip_flag:
        f = gzip.open(input_file, 'rt')
    else:
        f = open(input_file, 'r')

    query_num = query_num_start
    hit_num = hit_num_start
    hsp_num = hsp_num_start
    query_tmp = None
    for each_line in f:
        each_line = each_line.strip()
        info = each_line.split("\t")

        if query_tmp is None:
            new_query_flag = 1
            new_hit_flag = 1
        else:
            last_query_def = query_tmp.qDef
            last_hit_def = query_tmp.hit[-1].hit_def
            if last_query_def != info[0]:
                new_query_flag = 1
                new_hit_flag = 1
            else:
                new_query_flag = 0
                if last_hit_def != info[1]:
                    new_hit_flag = 1
                else:
                    new_hit_flag = 0

        if new_query_flag:
            if query_tmp is not None:
                # print(query_tmp)
                yield query_tmp

            query_num = query_num + 1
            query_tmp = BlastQuery(num=query_num, qID=info[0], qDef=info[0])
            # hit_num = 0

        if new_hit_flag:
            hit_num = hit_num + 1
            hit_tmp = BlastHit(hit_num=hit_num, query_num=query_num, hit_def=info[1], hit_accession=info[1])
            query_tmp.hit.append(hit_tmp)
            # hsp_num = 0

        hsp_num = hsp_num + 1
        hsp_tmp = BlastHsp(query_num=query_num, hsp_num=hsp_num, hit_num=hit_num, hsp_bit_score=float(info[11]),
                           hsp_evalue=float(info[10]), hsp_query_frame=int(info[6]), hsp_query_to=int(info[7]),
                           hsp_hit_from=int(info[8]), hsp_hit_to=int(info[9]), hsp_identity=float(info[2]),
                           hsp_gaps=int(info[5]), hsp_align_len=int(info[3]), hsp_mismatch=int(info[4]))

        # hsp_tmp.Hsp_mismatch = int(info[4])
        query_tmp.hit[-1].hsp.append(hsp_tmp)

    if query_tmp is not None:
        # print(query_tmp)
        yield query_tmp

    f.close()


def outfmt6_to_sqlite(outfmt6_file, db_file, gzip_flag=False, tmp_pool=10000, overwrite=False):
    db_file = os.path.abspath(db_file)

    if overwrite and os.path.exists(db_file):
        os.remove(db_file)

    db_file = "sqlite:///" + db_file

    engine = create_engine(db_file)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    query_num_start = session.query(BlastQuery).count()
    hit_num_start = session.query(BlastHit).count()
    hsp_num_start = session.query(BlastHsp).count()

    query_list_tmp = []
    for query_tmp in outfmt6_read_big(outfmt6_file, gzip_flag, query_num_start, hit_num_start, hsp_num_start):
        query_list_tmp.append(query_tmp)
        if len(query_list_tmp) >= tmp_pool:
            session.add_all(query_list_tmp)
            session.commit()
            query_list_tmp = []
    if not len(query_list_tmp) == 0:
        session.add_all(query_list_tmp)
        session.commit()

    session.close()


def get_blast_record(db_file, filter_para):
    """
    filter_para = {
        "query" : [],
        "hit" : []
    }
    """
    db_file = os.path.abspath(db_file)

    if not os.path.exists(db_file):
        raise EnvironmentError("failed found %s" % db_file)

    db_file = "sqlite:///" + db_file

    engine = create_engine(db_file)

    Session = sessionmaker(bind=engine)
    session = Session()

    query_list = session.query(BlastQuery).filter(BlastQuery.qDef.in_(filter_para['query'])).all()
    query_hsp = []
    for query in query_list:
        query_hsp.extend(query.hsp)

    subject_list = session.query(BlastHit).filter(BlastHit.hit_def.in_(filter_para['hit'])).all()
    subject_hsp = []
    for subject in subject_list:
        subject_hsp.extend(subject.hsp)

    session.close()

    if len(query_hsp) == 0:
        return subject_hsp
    elif len(subject_hsp) == 0:
        return query_hsp
    else:
        return list(set(query_hsp) & set(subject_hsp))

if __name__ == '__main__':
    outfmt6_file = '/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10/WorkingDirectory/Blast1_1.txt.gz'
    db_file = '/lustre/home/xuyuxing/Work/Csp/orthofinder/protein_seq/Results_Apr10/WorkingDirectory/test.db'

    outfmt6_to_sqlite(outfmt6_file, db_file, gzip_flag=True, tmp_pool=10000, overwrite=True)

