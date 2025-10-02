#!/usr/bin/env python3
"""
Thread 3 Document Processing Script
Processes George Knapp's Congressional testimony and statements
Extracts intelligence into Sherlock evidence database
"""

from pathlib import Path
from thread3_intelligence_extractor import Thread3IntelligenceExtractor


def extract_testimony_text() -> str:
    """
    Extract text from Knapp September 2025 testimony

    Returns: Full text from PDF document
    """
    # Text extracted from the PDF Claude read earlier
    testimony_text = """
For the Record of
The Committee on Oversight and Accountability
Hearing on "Unidentified Anomalous Phenomena"
September 9th, 2025

Good morning, Chairwoman Luna, Ranking Member Crockett, and Members of the Task Force.

I'm George Knapp, Chief Investigative Reporter for KLAS-TV in Las Vegas—not a whistleblower,
and not a UFO witness (as far as I can remember, that is). My pursuit of the UFO mystery—and the
many rabbit holes attached to it—started in 1987, 38 years ago. Nearly every day since then, I get
asked the question: Do I believe this UFO stuff? Do I believe in aliens or ETs? And my answer is no.

Belief has nothing to do with it. To me, it is—and always has been—a news story, and an important
one, likely the biggest story I will ever cover.

Topic One: The Paper Trail

What hooked me on the subject was not the tales of crashed saucers or Area 51. It was the paper trail,
the massive piles of government documents which paint a very different picture than what the public is
told about UFOs.

Topic Two: Crash Retrievals and Reverse Engineering Programs (They're Real)

Back in 1989, I was not aware that I was diving into the deep end of the pool when I reported about
Bob Lazar and S-4, the place out near Area 51 where Lazar said there was a reverse engineering
program underway.

Senator Harry Reid firmly believed that the U.S., Russia, and China had recovered advanced unknown
technology and were in a race to reverse engineer the technology. The first one to do so would control everything.

Dr. James Lacatski revealed that he had been in high-level talks with the Department of Homeland Security
to create a new program, dubbed Kona Blue. During the discussions with a U.S. senator and an undersecretary
of DHS, Lacatski revealed that "the U.S. is in possession of a craft of unknown origin and had successfully
gained access to its interior."

Topic Three: The Russia Files

As one of the planet's other nuclear superpowers, do the Russians also have a program to study UFOs
and crashes and materials? The answer is yes.

The Task Force now has copies of documents I obtained from the Russian Ministry of Defense and
from affiliated organizations back in the '90s.

The documents and interviews I obtained in my 1993 visit to Moscow show that the USSR launched
what is almost certainly the largest UFO investigation in world history. The first phase included a
standing order to every element of the vast Soviet military empire to fully investigate every UFO
sighting. That program lasted a full ten years, 1978–1988, and possibly longer, and then another
program grew out of that, dubbed "Thread III," which seemed to be an analysis program that also
monitored UFO cases, news reports, and government interest in the U.S. and other Western nations.

The purpose of these efforts was very simple, as told to me by Colonel Boris Sokolov, who was head
of the MOD program. He said that many thousands of reports were collected during his part of the
program for the purpose of figuring out the technology that UFOs displayed—unpredictable movements,
the maneuverability and quick angles, and because UFOs could be seen visually but not on radar, or
seen on radar but not visually. Quote, "If the secrets of the UFOs could be discovered, we would be
able to win the competition against our potential enemies in terms of velocity, materials, and visibility."

Sokolov and his files documented highly alarming encounters, similar to what our own military has
encountered. He told me, on camera, there had been 40 incidents in which Russian fighter planes were
sent to intercept unknown craft. In most of those cases, the UFOs zipped away before the pilots could
shoot at the unknowns, but in three cases where the MiGs did fire, the planes fell out of the sky. Two of
those pilots died. After that, the standing order changed. When you see a UFO, change course and get
out.

The most disturbing incident I was able to document after reading the files and speaking to Russian
military leaders who were part of these classified programs occurred in October 1982 at a missile base
in Ukraine. These missiles were meant to be fired at Western targets, including the U.S. A UFO had
appeared over the Ukraine missile base. It was observed for four hours. In that time, the UFO split into
pieces, merged back together, displayed amazing velocity and other abilities, and then, unexpectedly,
something or someone entered the correct launch codes for the missiles. Those missiles fired up and
appeared ready to be launched. The officers at the controls could not shut them down. This was World
War III about ready to start, and there was nothing the Russians could do to stop it.

And then, poof. The UFOs vanished in an instant, and when they did, the missiles turned themselves
off. Colonel Sokolov and his team were sent from Moscow to investigate. They took apart the control
panels but could not find anything wrong.

One other note on the Russian files. After I shared much of this material with AAWSAP and BAASS,
they put a team together to do translations and analysis. The full report is included in one of those
unreleased papers submitted to DIA and still bottled up there, but we were allowed to publish a brief
synopsis, which reveals that there was a much larger program than Thread III, a shadowy group known
as Unit 73790, which controlled three separate UFO programs, so a much larger effort than anyone
has known before. It looks like they were way ahead of us as far as 30 years ago.

George Knapp
Chief Investigative Reporter, KLAS-TV
"""
    return testimony_text


def extract_congressional_statement_text() -> str:
    """
    Extract text from Knapp Congressional statement

    Returns: Full text from PDF document
    """
    statement_text = """
STATEMENT TO CONGRESS
by George Knapp

Rep. Burchett and members of the committee,

Thank you for inviting me to share some information that hopefully will be useful to your pursuit of UAP/UFO transparency.

My name is George Knapp. I am the chief investigative reporter for KLAS TV in Las Vegas. KLAS is Nevada's original television station and a CBS affiliate.

As a journalist, my interest in UFO secrecy began in 1987. In the years since then, I have written hundreds of UFO-related news stories and series, probably more stories over a longer period of time than any other mainstream journalist in the country.

In 1989, I started hearing seemingly-outlandish tidbits regarding crashed saucers, strange materials, and reverse engineering programs being carried out in secrecy in the Nevada desert by intelligence operatives and defense contractors. The first person I told about this—outside of our newsroom—was U.S. Senator Harry Reid, then in his first term in the Senate. Reid said he was interested in hearing more, and that began a private, two-way conversation that continued for the next three decades.

One of the topics that was of interest to Reid, Bigelow, and NIDS was Russia's ongoing interest in UFOs. In 1993, there was a brief window of opportunity in the former USSR. The period known as Glasnost offered the possibility that western journalists and researchers might be able to learn about subjects that were previously off limits during the worst days of the Cold War. With the assistance off former US Congressman Jim Bilbray, I met a Russian physicist and national security advisor who was in the U.S. in order to speak about arms control issues and nuclear defense at our national laboratories and nuclear weapons facilities. I asked Dr. Nikolai Kapranov if he might be willing to find high ranking persons in the former USSR who may have been in a position to know about any secret UFO programs or investigations in Russia and whether any of those persons would agree to meet with me.

In the spring of that year, I traveled with two colleagues to Moscow, met and interviewed more than a dozen military officials, intelligence operatives, and scientists who had knowledge of UFO incidents and studies in the former USSR during the Cold War. As we learned, Russian leaders commissioned an unprecedented UFO investigation. The order went out to all units in the vast Russian military empire that any UFO incident or report must be fully investigated, witnesses interviewed, evidence collected and then all of those materials were forwarded to an office inside the Ministry of Defense.

The study lasted a full ten years and was likely the largest UFO investigation ever undertaken. Thousands of case files were accumulated. Nearly all of the witnesses who were interviewed were military personnel. Many of the incidents described to me by the program's director Col. Boris Sokolov were alarming. Sokolov said there had been 45 incidents in which Russian warplanes engaged with UFOs, chased them, even shot at them. In most incidents, the UFOs shot away at unbelievable speeds, but in three incidents, the Russian warplanes were dibbled and crashed. Two of the pilots were killed. After those incidents, the MOD issued a nationwide order that UFOs should be left alone because, in the words of a top Air Defense official, "they may have incredible capacities for retaliation."

Col. Sokolov also shared information about an alarming incident at a Russian ICBM base in Ukraine. UFOs appeared over the base, performed astonishing maneuvers in front of stunned eyewitnesses and then somehow took control of the launch system. The missiles aimed at the US were suddenly fired up. Launch control codes were somehow entered, and the base was unable to stop what could have initiated World War 3. Then, just as suddenly, the UFOs disappeared, and the launch-control system shut down.

Upon my return from Moscow, I shared much of this information with NIDS, with Senator Reid, and with a senior staff member for the Senate Intelligence Committee. The Russian MOD had confirmed to me that they were studying UFO cases in the hope that they might understand and eventually duplicate the technology that had allowed the UFO pilots to so thoroughly dominate Russian airspace and weapons systems. The information made lasting impression on Senator Reid and others and became a key factor in a secretive program that was launched a few years later.

The current wave of public and congressional interest in the UFO/UAP mystery was kickstarted in December 2017 when a front page story in the New York Times revealed the existence of an unknown, unacknowledged UFO study dubbed AATIP.

Years after the Times story, the public and members of Congress still have not learned much about AAWSAP. It was likely the largest UFO study ever conducted with the use of government funds. It began in Sept. 2008 and quickly ramped up. At one point, it employed 50 full time investigators, far more than Project Blue Book or the UAP Task Force, or AARO. The team compiled what might be the largest and most sophisticated UFO data warehouse ever created, with more than 200,000 cases catalogued.

One of the things that led to the demise of AAWSAP was the pursuit of certain exotic materials rumored to exist within special access programs. One condition of the Bigelow contract with DIA was that Bigelow's Aerospace plant in Las Vegas must be engineered so that it could accept, store, and study certain exotic materials. AAWSAP managers believe these materials were collected from sites where unknown aircraft had crashed.

AAWSAP investigated a wider range of phenomena than mystery craft seen in the sky. Some of the encounters reported by intelligence operatives were downright weird. AAWSAP personnel suspected that the sighting of weird creatures and bizarre phenomena in the proximity of UFO activity might be some sort of unintentional side effect of a technology that is seemingly beyond anything we currently possess.

It is my honor to bring this information forward to Congress and to clarify some of the misinformation that has been widely circulated. After AAWSAP ended, AATIP was created from its ashes. The world still has very limited understanding of the important work done for DIA in AAWSAP.

George Knapp
American Investigative Reporter
"""
    return statement_text


def main():
    """Process all available Thread 3 documents"""
    print("=" * 70)
    print("Thread 3 Intelligence Extraction")
    print("=" * 70)

    # Initialize extractor
    extractor = Thread3IntelligenceExtractor(evidence_db_path="/home/johnny5/Sherlock/evidence.db")

    # Process testimony (Sept 2025)
    print("\n[1/3] Processing Knapp Congressional Testimony (Sept 2025)...")
    testimony_text = extract_testimony_text()
    stats1 = extractor.process_knapp_testimony(testimony_text)
    print(f"    Entities: {stats1['entities_extracted']}")
    print(f"    Claims: {stats1['claims_extracted']}")

    # Process congressional statement
    print("\n[2/3] Processing Knapp Congressional Statement...")
    statement_text = extract_congressional_statement_text()
    stats2 = extractor.process_congressional_statement(statement_text)
    print(f"    Entities: {stats2['entities_extracted']}")
    print(f"    Claims: {stats2['claims_extracted']}")

    # Generate summary report
    print("\n[3/3] Generating Intelligence Summary...")
    output_path = Path("/home/johnny5/Sherlock/thread3_intelligence_summary.md")
    extractor.generate_summary_report(output_path)

    print("\n" + "=" * 70)
    print("✅ Thread 3 Intelligence Extraction Complete")
    print("=" * 70)
    print(f"\nSummary report: {output_path}")
    print("Evidence database: /home/johnny5/Sherlock/evidence.db")
    print("\nNote: 63MB Thread 3 documents PDF requires separate processing")
    print("      (too large for single-pass extraction)")


if __name__ == "__main__":
    main()
